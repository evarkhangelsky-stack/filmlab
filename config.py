import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", 0))

CITY = "moscow"
CURRENCY = "RUB"
CURRENCY_SYMBOL = "₽"

# Товары
PRODUCTS = {
    "5207": {
        "name": "KODAK 5207 / 250D",
        "price": 800,
        "description": "CINE ESTHETICS IN YOUR CAMERA."
    },
    "5219": {
        "name": "KODAK 5219 / 500T",
        "price": 850,
        "description": "Tungsten balanced for low light."
    }
}

# Способы оплаты (как на дизайне)
PAYMENT_METHODS = {
    "gal": "GAL (ECI)",
    "usdt_ton": "USDT/TON",
    "card": "CARD TRANSFER"
}

# Реквизиты
USDT_WALLET = "TX1x...XYZ"          # Ваш кошелёк USDT TRC20
CARD_DETAILS = "1234 5678 9012 3456\nИванов И.И."

# Время резерва (секунды)
RESERVE_SECONDS = 15 * 60  # 15 минут

# Станции метро для самовывоза
PICKUP_STATIONS = [
    "Курская (кольцевая)",
    "Павелецкая",
    "Таганская",
    "Киевская"
]

WELCOME_TEXT = "🎞 THE LAB\n\nВыберите действие:"
