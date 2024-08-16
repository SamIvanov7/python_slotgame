from django.contrib import admin
from .models import SlotMachine, Payline

@admin.register(Payline)
class PaylineAdmin(admin.ModelAdmin):
    list_display = ['slot_machine', 'line_number']
