import random
from decimal import Decimal
from .models import GameSession, Spin, Payline, Symbol, SlotMachine
from authentication.models import Transaction

DEFAULT_PAYLINES = [
    [(0, 0), (0, 1), (0, 2)],  # Line 1: Top row
    [(1, 0), (1, 1), (1, 2)],  # Line 2: Middle row
    [(2, 0), (2, 1), (2, 2)],  # Line 3: Bottom row
    [(0, 0), (1, 1), (2, 2)],  # Line 4: Diagonal from top left to bottom right
    [(0, 2), (1, 1), (2, 0)],  # Line 5: Diagonal from top right to bottom left
]

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
    """Generate a random slot machine spin using default symbol counts"""
    all_symbols = []
    for symbol, count in symbol_count.items():
        all_symbols.extend([symbol] * count)

    columns = []
    for _ in range(cols):
        column = random.sample(all_symbols, rows)
        columns.append(column)

    return columns


def get_paylines(slot_machine, lines):
    """Fetch custom paylines from the database or use default if none exist"""
    custom_paylines = Payline.objects.filter(slot_machine=slot_machine).order_by('line_number')[:lines]

    if custom_paylines.exists():
        paylines = [
            [(coord['row'], coord['col']) for coord in payline.coordinates]
            for payline in custom_paylines
        ]
    else:
        paylines = DEFAULT_PAYLINES[:lines]

    return paylines


def calculate_winnings(columns, slot_machine, lines, bet):
    """Calculate the total winnings based on spin results and paylines"""
    paylines = get_paylines(slot_machine, lines)
    winnings = Decimal(0)
    winning_lines = []

    for line_index, line in enumerate(paylines):
        symbol = columns[line[0][1]][line[0][0]]
        for position in line:
            row, col = position
            if col >= len(columns) or row >= len(columns[col]) or columns[col][row] != symbol:
                break
        else:
            winnings += Decimal(symbol_value.get(symbol, 0)) * Decimal(bet)
            winning_lines.append(line_index + 1)

    return winnings, winning_lines


def create_game_session(user, slot_machine, bet_amount, lines):
    """Create and return a new game session"""
    session = GameSession.objects.create(
        user=user,
        slot_machine=slot_machine,
        bet_amount=bet_amount,
        lines=lines
    )
    return session


def record_spin(session, result, winnings):
    """Record a completed spin and its results in the database"""
    spin = Spin.objects.create(
        game_session=session,
        spin_result=result,
        winnings=winnings
    )
    return spin


def create_bet_transaction(user, amount):
    """Record a bet transaction and update the user's balance"""
    new_balance = user.balance - amount
    Transaction.objects.create(
        user=user,
        transaction_type='BET',
        amount=amount,
        balance_after=new_balance
    )
    user.balance = new_balance
    user.save()


def create_win_transaction(user, amount):
    """Record a win transaction and update the user's balance"""
    new_balance = user.balance + amount
    Transaction.objects.create(
        user=user,
        transaction_type='WIN',
        amount=amount,
        balance_after=new_balance
    )
    user.balance = new_balance
    user.save()


def generate_spin(slot_machine):
    """Generate a random spin result for a slot machine using symbols from the database"""
    symbols = Symbol.objects.filter(slot_machine=slot_machine)
    symbol_pool = []

    for symbol in symbols:
        symbol_pool.extend([symbol.symbol_name] * symbol.symbol_count)

    # Generate the spin from the pool of symbols
    spin_result = random.choices(symbol_pool, k=slot_machine.rows * slot_machine.cols)
    return spin_result


# 
def calculate_rtp_and_volatility(slot_machine, total_spins=100000):
    """Calculate RTP and volatility by simulating a large number of spins"""
    symbols = Symbol.objects.filter(slot_machine=slot_machine)
    total_wins = Decimal(0)
    total_bets = Decimal(0)
    payout_distribution = []

    symbol_pool = []
    for symbol in symbols:
        symbol_pool.extend([symbol.symbol_name] * symbol.symbol_count)

    for _ in range(total_spins):
        bet_amount = Decimal(1)  # Пусть ставка на каждый спин будет $1.
        spin_result = random.choices(symbol_pool, k=slot_machine.rows * slot_machine.cols)

        winnings = calculate_winnings_from_simulation(spin_result, symbols, bet_amount)

        total_wins += winnings
        total_bets += bet_amount
        payout_distribution.append(winnings)

    rtp = (total_wins / total_bets) * 100

    average_payout = total_wins / total_spins
    variance = sum((x - average_payout) ** 2 for x in payout_distribution) / total_spins
    volatility = variance ** 0.5

    return rtp, volatility


# функция расчета выигрыша на основе симулированного результата спина
def calculate_winnings_from_simulation(spin_result, symbols, bet_amount):
    symbol_to_payout = {symbol.symbol_name: symbol.payout for symbol in symbols}

    # простая механика match-3 в целях симуляции
    winnings = Decimal(0)

    # простая проверка линий 
    for i in range(0, len(spin_result), 3):
        if spin_result[i:i + 3].count(spin_result[i]) == 3:
            winnings += symbol_to_payout.get(spin_result[i], Decimal(0)) * bet_amount

    return winnings
