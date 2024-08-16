from rest_framework import serializers
from .models import GameSession, Spin
from authentication.models import User

class BetSerializer(serializers.Serializer):
    slot_machine_id = serializers.IntegerField()
    bet_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    lines = serializers.IntegerField()

class SpinResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spin
        fields = ['spin_result', 'winnings', 'spin_time']
