from django.db import models
from django.utils import timezone
from authentication.models import User

class SlotMachine(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    cols = models.IntegerField()
    max_lines = models.IntegerField()
    min_bet = models.DecimalField(max_digits=10, decimal_places=2)
    max_bet = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot_machine = models.ForeignKey(SlotMachine, on_delete=models.CASCADE)
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    lines = models.IntegerField()
    total_winnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    session_start = models.DateTimeField(default=timezone.now)
    session_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.id} by {self.user}"


class Spin(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    spin_result = models.JSONField()  # Stores result of the spin as a JSON object
    winnings = models.DecimalField(max_digits=10, decimal_places=2)
    spin_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Spin {self.id} in Session {self.game_session.id}"