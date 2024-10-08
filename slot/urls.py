from django.urls import path
from .views import SlotMachineSpinView, PlayerBalanceView, DepositView

urlpatterns = [
    path('balance/', PlayerBalanceView.as_view(), name='player-balance'),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('spin/', SlotMachineSpinView.as_view(), name='slot-machine-spin'),
]
