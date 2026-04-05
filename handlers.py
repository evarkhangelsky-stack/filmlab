from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import (
    PRODUCTS, PAYMENT_METHODS, CURRENCY_SYMBOL, WELCOME_TEXT,
    CARD_DETAILS, USDT_WALLET, PICKUP_STATIONS
)
from database import add_to_cart, get_cart, remove_from_cart, set_quantity, clear_cart, create_order, get_user_orders
from keyboards import (
    main_menu_kb, catalog_kb, product_kb, cart_kb, payment_kb,
    my_orders_kb, order_detail_kb, back_to_catalog, pickup_stations_kb
)
from utils import format_cart
from admin_handlers import notify_admin_new_order
from states import OrderState

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb, parse_mode="Markdown")

@router.message(F.text == "🛍 MAIN MENU / SHOP")
async def shop_menu(message: Message):
    await message.answer("📋 *Каталог плёнок:*", reply_markup=catalog_kb(), parse_mode="Markdown")

@router.message(F.text == "🎞 LOAD REEL")
async def view_cart(message: Message):
    user_id = message.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await message.answer("🛒 Корзина пуста.", reply_markup=back_to_catalog)
        return
    text = format_cart(cart)
    await message.answer(text, reply_markup=cart_kb(user_id, cart), parse_mode="Markdown")

@router.message(F.text == "📜 MY ORDERS")
async def my_orders(message: Message):
    user_id = message.from_user.id
    orders = get_user_orders(user_id)
    if not orders:
        await message.answer("У вас пока нет заказов.")
        return
    await message.answer("📦 *Ваши заказы:*", reply_markup=my_orders_kb(orders), parse_mode="Markdown")

@router.message(F.text == "❓ FAQ & ECN-2")
async def faq(message: Message):
    await message.answer(
        "❓ *Часто задаваемые вопросы*\n\n"
        "1. **Как проявлять ECN-2?**\n"
        "   Рекомендуем использовать специальный набор.\n"
        "2. **Срок годности?**\n"
        "   Хранится в холодильнике до 2 лет.\n"
        "3. **Самовывоз**\n"
        f"   Станции метро: {', '.join(PICKUP_STATIONS[:3])} и другие.\n\n"
        "Подробнее спросите у оператора.",
        reply_markup=back_to_catalog, parse_mode="Markdown"
    )

@router.message(F.text == "📓 LAB NOTES")
async def lab_notes(message: Message):
    await message.answer(
        "📓 *Заметки лаборатории*\n\n"
        "Плёнка Kodak 5207 – легендарный материал. Обеспечивает мягкие тона и широкий динамический диапазон.\n"
        "Для проявки ECN-2 требуется удаление ретуши (rem-jet).",
        reply_markup=back_to_catalog, parse_mode="Markdown"
    )

@router.message(F.text == "📦 LOADING BAY INTRO")
async def loading_bay(message: Message):
    await message.answer(
        "🚚 *LOADING BAY*\n\n"
        "Здесь будет информация о новых поступлениях и статусе заказов.\n"
        "Следите за обновлениями!",
        reply_markup=back_to_catalog, parse_mode="Markdown"
    )

# ---------- Каталог ----------
@router.callback_query(F.data == "catalog")
async def show_catalog(callback: CallbackQuery):
    await callback.message.edit_text("📋 *Каталог плёнок:*", reply_markup=catalog_kb(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
async def show_product(callback: CallbackQuery):
    pid = callback.data.split("_")[1]
    product = PRODUCTS.get(pid)
    if not product:
        await callback.answer("Товар не найден")
        return
    text = f"*{product['name']}*\n\n{product['description']}\n\n💰 Цена: {product['price']} {CURRENCY_SYMBOL}"
    await callback.message.edit_text(text, reply_markup=product_kb(pid), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("add_"))
async def add_to_cart_handler(callback: CallbackQuery):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    add_to_cart(user_id, pid, 1)
    await callback.answer(f"✅ {PRODUCTS[pid]['name']} добавлен в корзину", show_alert=True)

# ---------- Корзина ----------
@router.callback_query(F.data == "view_cart")
async def show_cart_inline(callback: CallbackQuery):
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await callback.answer("Корзина пуста", show_alert=True)
        return
    text = format_cart(cart)
    await callback.message.edit_text(text, reply_markup=cart_kb(user_id, cart), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("inc_"))
async def increment_quantity(callback: CallbackQuery):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if pid in cart:
        new_qty = cart[pid] + 1
        set_quantity(user_id, pid, new_qty)
    await show_cart_inline(callback)

@router.callback_query(F.data.startswith("dec_"))
async def decrement_quantity(callback: CallbackQuery):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if pid in cart and cart[pid] > 1:
        new_qty = cart[pid] - 1
        set_quantity(user_id, pid, new_qty)
    elif pid in cart and cart[pid] == 1:
        remove_from_cart(user_id, pid)
    await show_cart_inline(callback)

@router.callback_query(F.data.startswith("del_"))
async def delete_item(callback: CallbackQuery):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    remove_from_cart(user_id, pid)
    await show_cart_inline(callback)

@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    clear_cart(user_id)
    await callback.message.edit_text("🛒 Корзина очищена.", reply_markup=back_to_catalog)
    await callback.answer()

@router.callback_query(F.data == "checkout")
async def checkout_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await callback.answer("Корзина пуста", show_alert=True)
        return
    await callback.message.edit_text("📍 Выберите станцию метро для самовывоза:", reply_markup=pickup_stations_kb())
    await state.set_state(OrderState.waiting_for_pickup_station)
    await callback.answer()

@router.callback_query(OrderState.waiting_for_pickup_station, F.data.startswith("station_"))
async def process_pickup_station(callback: CallbackQuery, state: FSMContext):
    station = callback.data.split("station_", 1)[1]
    await state.update_data(pickup_station=station)
    await callback.message.edit_text("Выберите способ оплаты:", reply_markup=payment_kb())
    await state.set_state(OrderState.waiting_for_payment_method)
    await callback.answer()

@router.callback_query(OrderState.waiting_for_payment_method, F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, state: FSMContext):
    method_code = callback.data.split("_")[1]  # card, usdt, manual
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await callback.message.edit_text("Корзина пуста.")
        await state.clear()
        return

    data = await state.get_data()
    pickup_station = data.get("pickup_station", "Не указана")

    subtotal = sum(PRODUCTS[pid]["price"] * qty for pid, qty in cart.items())
    total = subtotal   # доставка бесплатно (самовывоз)
    items = [{"id": pid, "qty": qty} for pid, qty in cart.items()]

    order_id = create_order(user_id, items, subtotal, total, method_code, pickup_station)

    await notify_admin_new_order(callback.bot, order_id, user_id, items, subtotal, total, method_code, pickup_station)
    
    # Показываем реквизиты
    if method_code == "usdt":
        await callback.message.edit_text(
            f"💰 *Оплата USDT (TRC20)*\n\n"
            f"Сумма: {total} {CURRENCY_SYMBOL} (в USDT по текущему курсу)\n"
            f"Кошелёк: `{USDT_WALLET}`\n"
            f"После оплаты нажмите 'Я оплатил'.\n\n"
            f"Заказ №{order_id}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"i_paid_{order_id}")]
            ])
        )
    elif method_code == "card":
        await callback.message.edit_text(
            f"💳 *Оплата картой*\n\n"
            f"Сумма: {total} {CURRENCY_SYMBOL}\n"
            f"Реквизиты: {CARD_DETAILS}\n"
            f"Заказ №{order_id}\n\nПосле перевода нажмите 'Я оплатил'.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"i_paid_{order_id}")]
            ])
        )
    else:  # manual
        await callback.message.edit_text(
            f"📱 *Ручной перевод*\n\n"
            f"Заказ №{order_id} принят. Менеджер свяжется с вами для уточнения оплаты и самовывоза.\n"
            f"Станция метро: {pickup_station}",
            reply_markup=back_to_catalog
        )
    await state.clear()

@router.callback_query(F.data.startswith("i_paid_"))
async def user_paid(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    from config import ADMIN_CHAT_ID
    await callback.bot.send_message(
        ADMIN_CHAT_ID,
        f"💰 Пользователь @{callback.from_user.username} (id:{callback.from_user.id}) сообщил об оплате заказа #{order_id}. Проверьте и подтвердите."
    )
    await callback.message.edit_text("Спасибо, ваш платёж проверяется. Мы свяжемся с вами.")
    await callback.answer()

# ---------- Мои заказы (детали) ----------
@router.callback_query(F.data == "my_orders")
async def show_my_orders(callback: CallbackQuery):
    user_id = callback.from_user.id
    orders = get_user_orders(user_id)
    if not orders:
        await callback.message.edit_text("У вас нет заказов.")
        return
    await callback.message.edit_text("📦 *Ваши заказы:*", reply_markup=my_orders_kb(orders), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("order_"))
async def order_detail(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    orders = get_user_orders(user_id)
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        await callback.answer("Заказ не найден")
        return
    items_text = "\n".join([f"{PRODUCTS[i['id']]['name']} x{i['qty']}" for i in order["items"]])
    status_rus = {
        "pending": "⏳ Ожидает оплаты",
        "paid": "✅ Оплачен",
        "shipped": "📦 Отправлен",
        "completed": "🏁 Завершён"
    }.get(order["status"], order["status"])
    text = f"*Заказ #{order_id}*\n\n{items_text}\n\nИтого: {order['total']} ₽\nСтатус: {status_rus}\nСамовывоз: {order['pickup_station']}"
    tracking = order.get("tracking_number")
    await callback.message.edit_text(text, reply_markup=order_detail_kb(order_id, tracking))
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Главное меню:", reply_markup=main_menu_kb)
    await callback.answer()

@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()
