from rest_framework import status
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from slot.models import SlotMachine
from slot.serializers import BetSerializer
from slot.services import (
    create_game_session, 
    generate_spin, 
    calculate_winnings, 
    record_spin, 
    create_bet_transaction, 
    create_win_transaction,
    calculate_rtp_and_volatility
)
from slot.services import DEFAULT_PAYLINES
from authentication.models import Transaction


class SlotMachineSpinView(APIView):
    def post(self, request):
        user = request.user
        serializer = BetSerializer(data=request.data)
        
        if serializer.is_valid():
            slot_machine_id = serializer.validated_data['slot_machine_id']
            bet_amount = serializer.validated_data['bet_amount']
            lines = serializer.validated_data['lines']
            
            slot_machine = get_object_or_404(SlotMachine, id=slot_machine_id)
            
            if bet_amount * lines > user.balance:
                return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
            
            if bet_amount < slot_machine.min_bet or bet_amount > slot_machine.max_bet:
                return Response({"error": f"Bet must be between {slot_machine.min_bet} and {slot_machine.max_bet}"}, status=status.HTTP_400_BAD_REQUEST)
            
            if lines > len(DEFAULT_PAYLINES) or lines < 1:
                return Response({"error": f"Invalid number of lines, max is {len(DEFAULT_PAYLINES)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            total_bet = bet_amount * lines
            create_bet_transaction(user, total_bet)
            
            session = create_game_session(user, slot_machine, bet_amount, lines)
            
            spin_result = generate_spin(slot_machine)
            
            winnings, winning_lines = calculate_winnings(spin_result, slot_machine, lines, bet_amount)
            
            record_spin(session, spin_result, winnings)
            
            if winnings > 0:
                create_win_transaction(user, winnings)

            return Response({
                "spin_result": spin_result,
                "winnings": winnings,
                "winning_lines": winning_lines,
                "balance": user.balance
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RTPVolatilityView(APIView):
    def get(self, request, slot_machine_id):
        slot_machine = get_object_or_404(SlotMachine, id=slot_machine_id)
        
        rtp, volatility = calculate_rtp_and_volatility(slot_machine)
        
        return Response({
            "rtp": rtp,
            "volatility": volatility
        }, status=status.HTTP_200_OK)


class PlayerBalanceView(APIView):
    def get(self, request):
        user = request.user
        return Response({"balance": user.balance}, status=status.HTTP_200_OK)


class DepositView(APIView):
    def post(self, request):
        user = request.user
        try:
            amount = Decimal(request.data.get("amount", 0))
            if amount <= 0:
                return Response({"error": "Deposit amount must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)
            
            user.balance += amount
            user.save()

            Transaction.objects.create(
                user=user,
                transaction_type='DEPOSIT',
                amount=amount,
                balance_after=user.balance
            )
            
            return Response({"message": "Deposit successful", "current_balance": user.balance}, status=status.HTTP_200_OK)
        
        except (TypeError, ValueError):
            return Response({"error": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST)
