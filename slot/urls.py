# slot/urls.py

from django.urls import path
from .views import SlotMachineSpinView

urlpatterns = [
    path('spin/', SlotMachineSpinView.as_view(), name='slot-machine-spin'),
]
