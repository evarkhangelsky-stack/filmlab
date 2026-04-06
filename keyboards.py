from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PRODUCTS, PAYMENT_METHODS, PICKUP_STATIONS

# Главное меню (кнопки для навигации)
main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Каталог", callback_data="main_catalog"),
     InlineKeyboardButton(text="🛒 Корзина", callback_data="main_cart")],
    [InlineKeyboardButton(text="📜 Мои заказы", callback_data="main_orders"),
     InlineKeyboardButton(text="❓ FAQ", callback_data="main_faq")],
    [InlineKeyboardButton(text="📓 Lab notes", callback_data="main_labnotes")]
])

# Каталог (список товаров)
def catalog_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for pid, info in PRODUCTS.items():
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"📷 {info['name']} — {info['price']} ₽",
                                 callback_data=f"product_{pid}")
        ])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 На главную", callback_data="main_menu")])
    return kb

# Карточка товара
def product_kb(product_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить в корзину", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton(text="🔙 В каталог", callback_data="main_catalog")]
    ])

# Корзина (динамическая)
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
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 На главную", callback_data="main_menu")])
    return kb

# Выбор метро
def pickup_stations_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for station in PICKUP_STATIONS:
        kb.inline_keyboard.append([InlineKeyboardButton(text=station, callback_data=f"station_{station}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="main_cart")])
    return kb

# Способы оплаты
def payment_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for code, name in PAYMENT_METHODS.items():
        kb.inline_keyboard.append([InlineKeyboardButton(text=name, callback_data=f"pay_{code}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="main_cart")])
    return kb

# Мои заказы (список)
def my_orders_kb(orders):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for order in orders:
        status_emoji = "⏳" if order["status"] == "pending" else "✅" if order["status"] == "paid" else "📦"
        text = f"{status_emoji} Заказ #{order['order_id']} - {order['total']}₽"
        kb.inline_keyboard.append([InlineKeyboardButton(text=text, callback_data=f"order_{order['order_id']}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 На главную", callback_data="main_menu")])
    return kb

def order_detail_kb(order_id: int, tracking=None):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    if tracking:
        kb.inline_keyboard.append([InlineKeyboardButton(text="📍 Отследить", url=f"https://www.pochta.ru/tracking/{tracking}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 К моим заказам", callback_data="main_orders")])
    return kb

# Клавиатура для карусели
def gallery_kb(current_index: int, total: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    nav_buttons = []
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀ Назад", callback_data="gallery_prev"))
    if current_index < total - 1:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ▶", callback_data="gallery_next"))
    if nav_buttons:
        kb.inline_keyboard.append(nav_buttons)
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")])
    return kb
