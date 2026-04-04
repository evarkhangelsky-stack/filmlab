from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import PRODUCTS, PAYMENT_METHODS, PICKUP_STATIONS

# Главное меню
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 MAIN MENU / SHOP")],
        [KeyboardButton(text="📦 LOADING BAY INTRO"), KeyboardButton(text="📜 MY ORDERS")],
        [KeyboardButton(text="❓ FAQ & ECN-2"), KeyboardButton(text="📓 LAB NOTES")],
        [KeyboardButton(text="🎞 LOAD REEL")]
    ],
    resize_keyboard=True
)

# Каталог
def catalog_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for pid, info in PRODUCTS.items():
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"📷 {info['name']} — {info['price']} ₽",
                                 callback_data=f"product_{pid}")
        ])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🛒 Корзина", callback_data="view_cart")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return kb

# Карточка товара
def product_kb(product_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить в корзину", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton(text="🔙 К каталогу", callback_data="catalog")]
    ])

# Корзина
def cart_kb(user_id: int, cart_data: dict):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for pid, qty in cart_data.items():
        name = PRODUCTS[pid]["name"][:20]
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="➖", callback_data=f"dec_{pid}"),
            InlineKeyboardButton(text=f"{name} x{qty}", callback_data="ignore"),
            InlineKeyboardButton(text="➕", callback_data=f"inc_{pid}"),
            InlineKeyboardButton(text="❌", callback_data=f"del_{pid}")
        ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="💳 Оформить заказ", callback_data="checkout"),
        InlineKeyboardButton(text="🗑 Очистить", callback_data="clear_cart")
    ])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 В каталог", callback_data="catalog")])
    return kb

# Выбор метро для самовывоза
def pickup_stations_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for station in PICKUP_STATIONS:
        kb.inline_keyboard.append([InlineKeyboardButton(text=station, callback_data=f"station_{station}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="view_cart")])
    return kb

# Способы оплаты
def payment_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for code, name in PAYMENT_METHODS.items():
        kb.inline_keyboard.append([InlineKeyboardButton(text=name, callback_data=f"pay_{code}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="view_cart")])
    return kb

# Мои заказы
def my_orders_kb(orders):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for order in orders:
        status_emoji = "⏳" if order["status"] == "pending" else "✅" if order["status"] == "paid" else "📦"
        text = f"{status_emoji} Заказ #{order['order_id']} - {order['total']}₽"
        kb.inline_keyboard.append([InlineKeyboardButton(text=text, callback_data=f"order_{order['order_id']}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return kb

def order_detail_kb(order_id: int, tracking=None):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    if tracking:
        kb.inline_keyboard.append([InlineKeyboardButton(text="📍 Отследить", url=f"https://www.pochta.ru/tracking/{tracking}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 К моим заказам", callback_data="my_orders")])
    return kb

back_to_catalog = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="catalog")]
])
