import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", 0))

CITY = "moscow"   # для Москвы

# Товары (цены в рублях)
PRODUCTS = {
    "5207": {
        "name": "KODAK 5207 / 250D",
        "price": 800,
        "description": "Cine esthetics in your camera. 35mm motion picture film."
    },
    "5219": {
        "name": "KODAK 5219 / 500T",
        "price": 850,
        "description": "Tungsten balanced, great for low light."
    }
    # Добавьте свои позиции
}

# Доставка: самовывоз (выбор метро)
DELIVERY_TYPE = "pickup"   # "pickup" или "courier"
PICKUP_STATIONS = [
    "Курская (кольцевая)",
    "Павелецкая",
    "Таганская",
    "Киевская",
    "Краснопресненская",
    "Белорусская",
    "Новослободская",
    "Проспект Мира",
    "Комсомольская",
    "Добрынинская",
    "Октябрьская"
]  # можно расширить

# Валюта
CURRENCY = "RUB"
CURRENCY_SYMBOL = "₽"

# Способы оплаты
PAYMENT_METHODS = {
    "card": "💳 Карта (СБП/МИР)",
    "usdt": "₿ USDT (TRC20)",
    "manual": "📱 Ручной перевод"
}

# Реквизиты (замените на свои)
CARD_DETAILS = "Номер карты: 1234 5678 9012 3456, получатель: Иван Иванов"
USDT_WALLET = "TX1x...XYZ"

WELCOME_TEXT = "🎞 Добро пожаловать в THE LAB (Москва)! Плёнки с самовывозом от метро."
