import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import (
    PRODUCTS, PAYMENT_METHODS, CURRENCY_SYMBOL, WELCOME_TEXT,
    USDT_WALLET, CARD_DETAILS, PICKUP_STATIONS, RESERVE_SECONDS
)
from database import (
    add_to_cart, get_cart, remove_from_cart, set_quantity,
    clear_cart, create_order, get_user_orders, update_order_status
)
from keyboards import (
    main_menu_kb, catalog_kb, product_kb, cart_kb,
    pickup_stations_kb, crypto_payment_kb, my_orders_kb, tracking_kb
)
from utils import format_cart_summary, format_usdt_amount
from admin_handlers import notify_admin_new_order
from states import OrderState, PaymentState

router = Router()

# Хранилище ID основного сообщения для каждого пользователя
user_main_msg = {}
# Хранилище задач таймера для отмены
user_timer_tasks = {}

async def update_main_message(bot: Bot, user_id: int, text: str, reply_markup=None):
    msg_id = user_main_msg.get(user_id)
    if msg_id:
        await bot.edit_message_text(text=text, chat_id=user_id, message_id=msg_id, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        msg = await bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup, parse_mode="Markdown")
        user_main_msg[user_id] = msg.message_id

async def delete_main_message(bot: Bot, user_id: int):
    msg_id = user_main_msg.pop(user_id, None)
    if msg_id:
        try:
            await bot.delete_message(chat_id=user_id, message_id=msg_id)
        except:
            pass

# ---------- СТАРТ ----------
@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    # Отменяем предыдущий таймер, если был
    task = user_timer_tasks.pop(message.from_user.id, None)
    if task:
        task.cancel()
    await update_main_message(bot, message.from_user.id, WELCOME_TEXT, reply_markup=main_menu_kb)

# ---------- ГЛАВНОЕ МЕНЮ ----------
@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    await update_main_message(bot, callback.from_user.id, WELCOME_TEXT, reply_markup=main_menu_kb)
    await callback.answer()

@router.callback_query(F.data == "main_shop")
async def show_catalog(callback: CallbackQuery, bot: Bot):
    await update_main_message(bot, callback.from_user.id, "📋 CATALOG", reply_markup=catalog_kb())
    await callback.answer()

@router.callback_query(F.data == "main_loading")
async def loading_bay(callback: CallbackQuery, bot: Bot):
    text = "🚚 LOADING BAY INTRO\n\nSoon: new film stocks and special offers."
    await update_main_message(bot, callback.from_user.id, text, reply_markup=main_menu_kb)
    await callback.answer()

@router.callback_query(F.data == "main_orders")
async def show_my_orders(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    orders = get_user_orders(user_id)
    if not orders:
        await update_main_message(bot, user_id, "No orders yet.", reply_markup=main_menu_kb)
    else:
        await update_main_message(bot, user_id, "📦 MY ORDERS", reply_markup=my_orders_kb(orders))
    await callback.answer()

@router.callback_query(F.data == "main_faq")
async def faq(callback: CallbackQuery, bot: Bot):
    text = "❓ FAQ & ECN-2\n\n1. How to develop ECN-2?\n2. Expiration: 2 years refrigerated.\n3. Pickup at metro stations."
    await update_main_message(bot, callback.from_user.id, text, reply_markup=main_menu_kb)
    await callback.answer()

@router.callback_query(F.data == "main_labnotes")
async def labnotes(callback: CallbackQuery, bot: Bot):
    text = "📓 LAB NOTES\n\nKodak 5207 / 250D provides soft tones and wide dynamic range. Rem-jet removal required."
    await update_main_message(bot, callback.from_user.id, text, reply_markup=main_menu_kb)
    await callback.answer()

@router.callback_query(F.data == "main_cart")
async def show_cart(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await update_main_message(bot, user_id, "Your reel is empty.", reply_markup=main_menu_kb)
        await callback.answer()
        return
    subtotal = sum(PRODUCTS[pid]["price"] * qty for pid, qty in cart.items())
    # Форматируем корзину в стиле ORDER SUMMARY
    text = format_cart_summary(cart, subtotal)
    # Время резерва (15 минут)
    reserve_str = "14:59"  # позже динамически
    kb, reserve_text = cart_kb(user_id, cart, subtotal, reserve_str)
    text += f"\n\n{reserve_text}"
    await update_main_message(bot, user_id, text, reply_markup=kb)
    await callback.answer()

# ---------- КАТАЛОГ ----------
@router.callback_query(F.data.startswith("product_"))
async def show_product(callback: CallbackQuery, bot: Bot):
    pid = callback.data.split("_")[1]
    product = PRODUCTS.get(pid)
    text = f"VISION3 {product['name']}\n{product['price']} {CURRENCY_SYMBOL}\n\n{product['description']}"
    await update_main_message(bot, callback.from_user.id, text, reply_markup=product_kb(pid))
    await callback.answer()

@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery, bot: Bot):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    add_to_cart(user_id, pid, 1)
    await callback.answer(f"Added {PRODUCTS[pid]['name']} to reel", show_alert=True)
    # Остаёмся на карточке товара
    await show_product(callback, bot)

# ---------- КОРЗИНА (управление количеством) ----------
@router.callback_query(F.data.startswith("inc_"))
async def inc_qty(callback: CallbackQuery, bot: Bot):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if pid in cart:
        set_quantity(user_id, pid, cart[pid] + 1)
    await show_cart(callback, bot, None)

@router.callback_query(F.data.startswith("dec_"))
async def dec_qty(callback: CallbackQuery, bot: Bot):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if pid in cart and cart[pid] > 1:
        set_quantity(user_id, pid, cart[pid] - 1)
    elif pid in cart and cart[pid] == 1:
        remove_from_cart(user_id, pid)
    await show_cart(callback, bot, None)

@router.callback_query(F.data.startswith("del_"))
async def del_item(callback: CallbackQuery, bot: Bot):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    remove_from_cart(user_id, pid)
    await show_cart(callback, bot, None)

@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    clear_cart(user_id)
    await update_main_message(bot, user_id, "Your reel is empty.", reply_markup=main_menu_kb)
    await callback.answer()

# ---------- ОФОРМЛЕНИЕ ЗАКАЗА (выбор метро и оплаты) ----------
@router.callback_query(F.data == "checkout")
async def checkout_start(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await callback.answer("Reel is empty", show_alert=True)
        return
    await update_main_message(bot, user_id, "📍 Choose pickup metro station:", reply_markup=pickup_stations_kb())
    await state.set_state(OrderState.waiting_for_pickup_station)
    await callback.answer()

@router.callback_query(OrderState.waiting_for_pickup_station, F.data.startswith("station_"))
async def process_pickup(callback: CallbackQuery, state: FSMContext, bot: Bot):
    station = callback.data.split("station_", 1)[1]
    await state.update_data(pickup_station=station)
    # Показываем выбор оплаты (как на дизайне)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="GAL (ECI)", callback_data="pay_gal")],
        [InlineKeyboardButton(text="USDT/TON", callback_data="pay_usdt_ton")],
        [InlineKeyboardButton(text="CARD TRANSFER", callback_data="pay_card")],
        [InlineKeyboardButton(text="◀ BACK", callback_data="main_cart")]
    ])
    await update_main_message(bot, callback.from_user.id, "💳 SELECT PAYMENT METHOD:", reply_markup=kb)
    await state.set_state(OrderState.waiting_for_payment_method)
    await callback.answer()

@router.callback_query(OrderState.waiting_for_payment_method, F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, state: FSMContext, bot: Bot):
    method_code = callback.data.split("_")[1]  # gal, usdt_ton, card
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await update_main_message(bot, user_id, "Reel empty.", reply_markup=main_menu_kb)
        await state.clear()
        return

    data = await state.get_data()
    pickup_station = data.get("pickup_station", "Not specified")

    subtotal = sum(PRODUCTS[pid]["price"] * qty for pid, qty in cart.items())
    total = subtotal
    items = [{"id": pid, "qty": qty} for pid, qty in cart.items()]

    # Создаём заказ со статусом pending
    order_id = create_order(user_id, items, subtotal, total, method_code, pickup_station)

    # Уведомляем админа
    await notify_admin_new_order(bot, order_id, user_id, items, subtotal, total, method_code, pickup_station)

    if method_code == "usdt_ton":
        # Рассчитываем сумму в USDT (допустим курс 1 USDT = 90 RUB)
        usdt_amount = round(total / 90, 2)
        text = (
            f"🔐 CRYPTO VAULT PAYMENT\nUSDT TRC20\n\n"
            f"SEND EXACTLY {usdt_amount} USDT\n(including fee).\n\n"
            f"WALLET: `{USDT_WALLET}`\n\n"
            f"WAITING FOR BLOCKCHAIN CONFIRMATION...\n\n"
            f"Order #{order_id} reserved for 15 minutes."
        )
        kb = crypto_payment_kb(order_id, str(usdt_amount))
        await update_main_message(bot, user_id, text, reply_markup=kb)
        # Запускаем таймер на отмену заказа через RESERVE_SECONDS
        await start_reserve_timer(bot, user_id, order_id, state)
        await state.set_state(PaymentState.usdt_waiting)
        await state.update_data(order_id=order_id)
    elif method_code == "card":
        text = (
            f"💳 CARD TRANSFER\n\n"
            f"Total: {total} {CURRENCY_SYMBOL}\n"
            f"Card details:\n{CARD_DETAILS}\n\n"
            f"After transfer press 'I PAID'.\nOrder #{order_id}"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ I PAID", callback_data=f"i_paid_{order_id}")],
            [InlineKeyboardButton(text="◀ CANCEL", callback_data="main_menu")]
        ])
        await update_main_message(bot, user_id, text, reply_markup=kb)
    else:  # gal (ручной перевод)
        text = f"📱 GAL (ECI) – manual transfer\n\nOrder #{order_id} accepted. Manager will contact you.\nPickup: {pickup_station}"
        await update_main_message(bot, user_id, text, reply_markup=main_menu_kb)
    await state.clear()  # очищаем состояние, но для USDT таймер работает отдельно

async def start_reserve_timer(bot: Bot, user_id: int, order_id: int, state: FSMContext):
    # Отменяем предыдущий таймер
    prev = user_timer_tasks.pop(user_id, None)
    if prev:
        prev.cancel()
    # Создаём новую задачу
    task = asyncio.create_task(reserve_timer(bot, user_id, order_id, state))
    user_timer_tasks[user_id] = task

async def reserve_timer(bot: Bot, user_id: int, order_id: int, state: FSMContext):
    remaining = RESERVE_SECONDS
    while remaining > 0:
        await asyncio.sleep(1)
        remaining -= 1
        # Обновляем сообщение с таймером, если пользователь всё ещё на странице оплаты
        # Для простоты не будем обновлять каждую секунду, только по истечении
    # Время вышло
    # Отменяем заказ и очищаем корзину
    from database import update_order_status, clear_cart
    update_order_status(order_id, "cancelled")
    clear_cart(user_id)
    await bot.send_message(user_id, "⏰ Reservation time expired. Your order has been cancelled.")
    # Возвращаем в главное меню
    await update_main_message(bot, user_id, WELCOME_TEXT, reply_markup=main_menu_kb)
    user_timer_tasks.pop(user_id, None)

@router.callback_query(F.data.startswith("i_paid_"))
async def user_paid(callback: CallbackQuery, bot: Bot, state: FSMContext):
    order_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    # Отменяем таймер
    task = user_timer_tasks.pop(user_id, None)
    if task:
        task.cancel()
    # Уведомляем админа
    from config import ADMIN_CHAT_ID
    await bot.send_message(ADMIN_CHAT_ID, f"💰 User @{callback.from_user.username} (id:{user_id}) reported payment for order #{order_id}.")
    await update_main_message(bot, user_id, "✅ Thank you! We will verify the payment and notify you.", reply_markup=main_menu_kb)
    await callback.answer()

# ---------- ДЕТАЛИ ЗАКАЗА И ТРЕКИНГ ----------
@router.callback_query(F.data.startswith("order_"))
async def order_detail(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    orders = get_user_orders(user_id)
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        await callback.answer("Order not found")
        return
    items_text = "\n".join([f"{PRODUCTS[i['id']]['name']} x{i['qty']}" for i in order["items"]])
    status_rus = {"pending": "⏳ AWAITING PAYMENT", "paid": "✅ PAID", "shipped": "📦 ON THE ROAD", "cancelled": "❌ CANCELLED"}.get(order["status"], order["status"])
    text = (
        f"ORDER #{order_id}\n\n"
        f"{items_text}\n\n"
        f"Total: {order['total']} {CURRENCY_SYMBOL}\n"
        f"Status: {status_rus}\n"
        f"Pickup: {order['pickup_station']}\n"
    )
    if order.get("tracking_number"):
        text += f"\nTRACKING #: {order['tracking_number']}\nSt. Petersburg"
        kb = tracking_kb(order['tracking_number'], "St. Petersburg")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀ BACK", callback_data="main_orders")]])
    await update_main_message(bot, user_id, text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "ignore")
async def ignore(callback: CallbackQuery):
    await callback.answer()
