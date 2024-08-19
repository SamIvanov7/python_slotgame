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
    """
    Генерирует случайный результат спина игрового автомата, используя 
    заданные символы и их количество.
    """
    all_symbols = []
    # Собираем все символы в один список в соответствии с их количеством
    for symbol, count in symbol_count.items():
        all_symbols.extend([symbol] * count)

    columns = []
    # Генерируем случайные символы для каждой колонки игрового автомата
    for _ in range(cols):
        column = random.sample(all_symbols, rows)
        columns.append(column)

    return columns


def get_paylines(slot_machine, lines):
    """
    Получает линии выплат для игрового автомата. Если есть кастомные линии в базе, 
    использует их, иначе возвращает стандартные линии.
    """
    custom_paylines = Payline.objects.filter(slot_machine=slot_machine).order_by('line_number')[:lines]

    if custom_paylines.exists():
        # Если есть кастомные линии, преобразуем их из JSON в список координат
        paylines = [
            [(coord['row'], coord['col']) for coord in payline.coordinates]
            for payline in custom_paylines
        ]
    else:
        # Если кастомных линий нет, используем стандартные
        paylines = DEFAULT_PAYLINES[:lines]

    return paylines


def calculate_winnings(columns, slot_machine, lines, bet):
    """
    Рассчитывает выигрыш по результатам спина и выбранным линиям выплат.
    """
    paylines = get_paylines(slot_machine, lines)
    winnings = Decimal(0)
    winning_lines = []

    # Проверяем каждую линию на совпадение символов
    for line_index, line in enumerate(paylines):
        symbol = columns[line[0][1]][line[0][0]]  # Первый символ в линии
        for position in line:
            row, col = position
            if col >= len(columns) or row >= len(columns[col]) or columns[col][row] != symbol:
                break
        else:
            # Если все символы на линии совпали, начисляем выигрыш
            winnings += Decimal(symbol_value.get(symbol, 0)) * Decimal(bet)
            winning_lines.append(line_index + 1)

    return winnings, winning_lines


def create_game_session(user, slot_machine, bet_amount, lines):
    """
    Создает новую игровую сессию для пользователя и сохраняет её в базе данных.
    """
    session = GameSession.objects.create(
        user=user,
        slot_machine=slot_machine,
        bet_amount=bet_amount,
        lines=lines
    )
    return session


def record_spin(session, result, winnings):
    """
    Сохраняет информацию о спине (результате вращения) в базе данных.
    """
    spin = Spin.objects.create(
        game_session=session,
        spin_result=result,
        winnings=winnings
    )
    return spin


def create_bet_transaction(user, amount):
    """
    Сохраняет транзакцию ставки и обновляет баланс пользователя.
    """
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
    """
    Сохраняет транзакцию выигрыша и обновляет баланс пользователя.
    """
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
    """
    Генерирует случайный результат спина для игрового автомата, используя символы из базы данных.
    """
    symbols = Symbol.objects.filter(slot_machine=slot_machine)
    symbol_pool = []

    # пул символов на основе их частоты
    for symbol in symbols:
        symbol_pool.extend([symbol.symbol_name] * symbol.symbol_count)

    # генерируем случайный результат спина
    spin_result = random.choices(symbol_pool, k=slot_machine.rows * slot_machine.cols)
    return spin_result


def calculate_rtp_and_volatility(slot_machine, total_spins=100000):
    """
    Рассчет RTP и волатильность игрового автомата.

    Параметры:
    - slot_machine: объект SlotMachine, для которого будет проведен расчет.
    - total_spins: количество симулируемых спинов (по умолчанию 100000).

    return:
    - rtp: процент возврата игроку, который показывает, сколько денег автомат возвращает в среднем.
    - volatility: волатильность, показывающая, насколько сильно варьируются выплаты.
    """
    # получаем все символы, которые используются в данном игровом автомате
    symbols = Symbol.objects.filter(slot_machine=slot_machine)
    
    # переменные для накопления общей суммы выигрышей и ставок
    total_wins = Decimal(0)
    total_bets = Decimal(0)
    
    # список для хранения всех выигрышей, что будет использован для расчета волатильности
    payout_distribution = []

    #  пул символов, где каждый символ повторяется в зависимости от его частоты (symbol_count)
    symbol_pool = []
    for symbol in symbols:
        symbol_pool.extend([symbol.symbol_name] * symbol.symbol_count)

    # старт симуляции заданного total_spins
    for _ in range(total_spins):
        # Задаем фиксированную ставку $1 на каждый спин
        bet_amount = Decimal(1)
        
        # генерим результат спина
        spin_result = random.choices(symbol_pool, k=slot_machine.rows * slot_machine.cols)

        # рассчет выигрыша спина на основе результата
        winnings = calculate_winnings_from_simulation(spin_result, symbols, bet_amount)

        # добавляем выигрыш к общей сумме выигрышей
        total_wins += winnings
        
        # добавляем ставку к общей сумме ставок
        total_bets += bet_amount
        
        # сохраняем размер выигрыша для дальнейшего анализа волатильности
        payout_distribution.append(winnings)

    # считааем RTP как отношение общей суммы выигрышей к общей сумме ставок
    # это показывает процент возврата игроку
    rtp = (total_wins / total_bets) * 100

    # рассчет среднего выигрыша за спин (average_payout)
    average_payout = total_wins / total_spins
    
    # рассчитываем дисперсию (variance) — отклонение всех выплат от среднего значения
    # она показывает насколько сильно выплаты варируются вокруг среднего значения
    variance = sum((x - average_payout) ** 2 for x in payout_distribution) / total_spins
    
    # волатильность — это квадратный корень из дисперсии, который показывает, насколько сильно выплаты отличаются от среднего значения
    volatility = variance ** 0.5

    return rtp, volatility


def calculate_winnings_from_simulation(spin_result, symbols, bet_amount):
    """
    Рассчитывает выигрыш на основе результата симуляции спина. 
    Используется простая механика "match-3", когда нужно совпадение 
    трех одинаковых символов подряд для получения выигрыша.

    Параметры:
    - spin_result: список символов, полученных в результате спина
    - symbols: все символы и их выплаты
    - bet_amount: ставка, сделанная на спин

    Возвращает:
    - winnings: итоговый выигрыш на основе совпадений символов.
    """
    # словарь, где каждому символу сопоставляем его выплату
    symbol_to_payout = {symbol.symbol_name: symbol.payout for symbol in symbols}

    # переменнаю для накопления выигрыша
    winnings = Decimal(0)

    # Проходим по результатам спина, проверяя каждые три символа на совпадение
    for i in range(0, len(spin_result), 3):
        # проверяем, совпадают ли три символа подряд
        if spin_result[i:i + 3].count(spin_result[i]) == 3:
            # если все три символа совпадают, добавляем соответствующую выплату за этот символ
            winnings += symbol_to_payout.get(spin_result[i], Decimal(0)) * bet_amount

    # возвращаем общий выигрыш за этот спин
    return winnings

