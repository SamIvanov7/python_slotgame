# slot/services.py

import random
from .models import GameSession, Spin
from decimal import Decimal

symbol_count = {
    "Apple": 2,
    "Banana": 4,
    "Citrus": 6,
    "Strawberry": 8
}

symbol_value = {
    "Apple": 5,
    "Banana": 4,
    "Citrus": 3,
    "Strawberry": 2
}

def get_slot_machine_spin(rows, cols):
    """Generate a random slot machine spin."""
    all_symbols = []
    for symbol, count in symbol_count.items():
        all_symbols.extend([symbol] * count)
    
    columns = []
    for _ in range(cols):
        column = random.sample(all_symbols, rows)
        columns.append(column)
    
    return columns

def calculate_winnings(columns, lines, bet):
    """Calculate winnings based on slot machine spin."""
    winnings = Decimal(0)
    winning_lines = []

    for line in range(lines):
        symbol = columns[0][line]
        for column in columns:
            if column[line] != symbol:
                break
        else:
            winnings += Decimal(symbol_value[symbol]) * Decimal(bet)
            winning_lines.append(line + 1)

    return winnings, winning_lines

def create_game_session(user, slot_machine, bet_amount, lines):
    """Create a new game session."""
    session = GameSession.objects.create(
        user=user,
        slot_machine=slot_machine,
        bet_amount=bet_amount,
        lines=lines
    )
    return session

def record_spin(session, result, winnings):
    """Record a spin in the database."""
    spin = Spin.objects.create(
        game_session=session,
        spin_result=result,
        winnings=winnings
    )
    return spin
