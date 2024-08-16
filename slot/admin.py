from django.contrib import admin
from .models import SlotMachine, Symbol, GameSession, Spin, Payline

class SlotMachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'rows', 'cols', 'max_lines', 'min_bet', 'max_bet', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

class SymbolAdmin(admin.ModelAdmin):
    list_display = ('slot_machine', 'symbol_name', 'symbol_count', 'payout')
    list_filter = ('slot_machine',)
    search_fields = ('symbol_name', 'slot_machine__name')
    ordering = ('slot_machine', 'symbol_name')

class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'slot_machine', 'bet_amount', 'lines', 'total_winnings', 'session_start', 'session_end')
    list_filter = ('session_start', 'session_end', 'slot_machine')
    search_fields = ('user__email', 'slot_machine__name')
    ordering = ('-session_start',)
    readonly_fields = ('session_start', 'session_end')

class SpinAdmin(admin.ModelAdmin):
    list_display = ('game_session', 'spin_result', 'winnings', 'spin_time')
    list_filter = ('spin_time',)
    search_fields = ('game_session__user__email',)
    ordering = ('-spin_time',)
    readonly_fields = ('spin_time',)

class PaylineAdmin(admin.ModelAdmin):
    list_display = ('slot_machine', 'line_number', 'coordinates')
    list_filter = ('slot_machine',)
    search_fields = ('slot_machine__name',)
    ordering = ('slot_machine', 'line_number')


admin.site.register(SlotMachine, SlotMachineAdmin)
admin.site.register(Symbol, SymbolAdmin)
admin.site.register(GameSession, GameSessionAdmin)
admin.site.register(Spin, SpinAdmin)
admin.site.register(Payline, PaylineAdmin)
