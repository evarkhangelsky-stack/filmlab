from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PRODUCTS, PAYMENT_METHODS, PICKUP_STATIONS

# ----- Главное меню (как на картинке) -----
main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="MAIN MENU / SHOP", callback_data="main_shop")],
    [InlineKeyboardButton(text="LOADING BAY INTRO", callback_data="main_loading")],
    [InlineKeyboardButton(text="MY ORDERS", callback_data="main_orders")],
    [InlineKeyboardButton(text="FAQ & ECN-2", callback_data="main_faq")],
    [InlineKeyboardButton(text="LAB NOTES", callback_data="main_labnotes")],
    [InlineKeyboardButton(text="LOAD REEL", callback_data="main_cart")]
])

# ----- Каталог (список товаров) -----
def catalog_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for pid, info in PRODUCTS.items():
        kb.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{info['name']}  {info['price']} {CURRENCY_SYMBOL}",
                callback_data=f"product_{pid}"
            )
        ])
    kb.inline_keyboard.append([InlineKeyboardButton(text="◀ BACK", callback_data="main_menu")])
    return kb

# ----- Карточка товара -----
def product_kb(product_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ ADD TO REEL", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton(text="◀ BACK TO SHOP", callback_data="main_shop")]
    ])

# ----- Корзина / ORDER SUMMARY -----
def cart_kb(user_id: int, cart_data: dict, total: int, reserve_time_str: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for pid, qty in cart_data.items():
        name = PRODUCTS[pid]["name"][:15]
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="−", callback_data=f"dec_{pid}"),
            InlineKeyboardButton(text=f"{name} x{qty}", callback_data="ignore"),
            InlineKeyboardButton(text="+", callback_data=f"inc_{pid}"),
            InlineKeyboardButton(text="🗑", callback_data=f"del_{pid}")
        ])
    # Способы оплаты как на дизайне
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="GAL (ECI)", callback_data="pay_gal"),
        InlineKeyboardButton(text="USDT/TON", callback_data="pay_usdt_ton"),
        InlineKeyboardButton(text="CARD TRANSFER", callback_data="pay_card")
    ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="🗑 CLEAR CART", callback_data="clear_cart"),
        InlineKeyboardButton(text="◀ BACK", callback_data="main_menu")
    ])
    # Добавляем информацию о резерве
    return kb, f"RESERVED FOR {reserve_time_str}"

# ----- Выбор метро (перед оплатой) -----
def pickup_stations_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for station in PICKUP_STATIONS:
        kb.inline_keyboard.append([InlineKeyboardButton(text=station, callback_data=f"station_{station}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="◀ BACK", callback_data="main_cart")])
    return kb

# ----- Страница криптооплаты (USDT TRC20) -----
def crypto_payment_kb(order_id: int, total_usdt: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ I PAID", callback_data=f"i_paid_{order_id}")],
        [InlineKeyboardButton(text="◀ CANCEL", callback_data="main_menu")]
    ])
    return kb

# ----- Мои заказы (список) -----
def my_orders_kb(orders):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for order in orders:
        status_emoji = "⏳" if order["status"] == "pending" else "✅" if order["status"] == "paid" else "📦"
        text = f"{status_emoji} ORDER #{order['order_id']} – {order['total']} {CURRENCY_SYMBOL}"
        kb.inline_keyboard.append([InlineKeyboardButton(text=text, callback_data=f"order_{order['order_id']}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="◀ BACK", callback_data="main_menu")])
    return kb

# ----- Детали заказа с трекингом (как на дизайне) -----
def tracking_kb(tracking_number: str, location: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 GOOGLE MAPS", url=f"https://maps.google.com/?q={location}")],
        [InlineKeyboardButton(text="◀ BACK TO ORDERS", callback_data="main_orders")]
    ])
    return kb
