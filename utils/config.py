import toml

with open('config.toml', 'r', encoding='utf-8') as f:
    config = toml.load(f)


settings = config.get('MAIN')

SOL_RPC_URL = settings['SOL_RPC_URL']
MAX_RETRIES = settings['MAX_RETRIES']

# Время ожидания между выполнением разных акков рандомное в указанном диапазоне
NEXT_ADDRESS_WAIT_TIME = settings['NEXT_ADDRESS_WAIT_TIME']  # В минутах

# Время ожидания между действиями одного аккаунта
NEXT_TX_WAIT_TIME = settings['NEXT_TX_WAIT_TIME']   # В секундах

# -----------------------------------------JUPITER----------------------------------------- #

settings = config.get('SWAP')

# "USDC", "USDT", "JUP", "SOL", "BONK"
SWAP_FROM = settings['SWAP_FROM']
SWAP_TO = settings['SWAP_TO']

# Количество транзакций на каждый аккаунт рандомное в указанном диапазоне
TX_COUNT = settings['TX_COUNT']

# Минимальное количество токена, которую ищет скрипт среди списка SWAP_FROM
BALANCE_MIN_AMOUNT = settings['BALANCE_MIN_AMOUNT']
# Сколько процентов от баланса свапать. Рандомизируется в пределах погрешности
SWAP_AMOUNT_PERCENT = settings['SWAP_AMOUNT_PERCENT']
# Максимальная погрешность в проценте
MAX_SWAP_AMOUNT_PERCENT_INACCURACY = settings['MAX_SWAP_AMOUNT_PERCENT_INACCURACY']

SLIPPAGE_BPS = settings['SLIPPAGE_BPS']

settings = config.get('VOTE')
