from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import SlotMachine, GameSession
from .serializers import BetSerializer, SpinResultSerializer
from .services import get_slot_machine_spin, calculate_winnings, create_game_session, record_spin, DEFAULT_PAYLINES

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            amount = float(request.data.get("amount", 0))
            if amount <= 0:
                return Response({"error": "Deposit amount must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

            # Update the user's balance
            user.balance += amount
            user.save()

            return Response({"message": "Deposit successful", "current_balance": user.balance}, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST)

class PlayerBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({"balance": user.balance}, status=200)


class SlotMachineSpinView(APIView):
    def post(self, request):
        user = request.user
        serializer = BetSerializer(data=request.data)
        
        if serializer.is_valid():
            slot_machine_id = serializer.validated_data['slot_machine_id']
            bet_amount = serializer.validated_data['bet_amount']
            lines = serializer.validated_data['lines']
            
            # Validate slot machine and bet
            slot_machine = get_object_or_404(SlotMachine, id=slot_machine_id)
            if bet_amount > user.balance:
                return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
            
            if bet_amount < slot_machine.min_bet or bet_amount > slot_machine.max_bet:
                return Response({"error": "Invalid bet amount"}, status=status.HTTP_400_BAD_REQUEST)
            
            if lines > len(DEFAULT_PAYLINES) or lines < 1:
                return Response({"error": "Invalid number of lines"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Deduct balance and create session
            user.balance -= bet_amount * lines
            user.save()
            
            session = create_game_session(user, slot_machine, bet_amount, lines)
            
            # Perform slot machine spin
            spin_result = get_slot_machine_spin(slot_machine.rows, slot_machine.cols)
            winnings, winning_lines = calculate_winnings(spin_result, slot_machine, lines, bet_amount)
            
            # Record spin and update balance
            record_spin(session, spin_result, winnings)
            user.balance += winnings
            user.save()

            return Response({
                "spin_result": spin_result,
                "winnings": winnings,
                "winning_lines": winning_lines,
                "balance": user.balance
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)