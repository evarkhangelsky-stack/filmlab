from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import PRODUCTS, PAYMENT_METHODS, CURRENCY_SYMBOL, WELCOME_TEXT, CARD_DETAILS, USDT_WALLET, PICKUP_STATIONS, GALLERY_ITEMS
from database import add_to_cart, get_cart, remove_from_cart, set_quantity, clear_cart, create_order, get_user_orders
from keyboards import (
    main_menu_kb, catalog_kb, product_kb, cart_kb, payment_kb,
    my_orders_kb, order_detail_kb, pickup_stations_kb, gallery_kb
)
from utils import format_cart
from admin_handlers import notify_admin_new_order
from states import OrderState, GalleryState

router = Router()

# Хранилище ID основного сообщения для каждого пользователя
user_main_msg = {}

async def update_main_message(bot: Bot, user_id: int, text: str, reply_markup=None, photo=None):
    """Редактирует основное сообщение или отправляет новое, если ещё нет."""
    msg_id = user_main_msg.get(user_id)
    if msg_id:
        if photo:
            # Если нужно поменять фото (карусель)
            media = InputMediaPhoto(media=photo, caption=text)
            await bot.edit_message_media(media=media, chat_id=user_id, message_id=msg_id, reply_markup=reply_markup)
        else:
            await bot.edit_message_text(text=text, chat_id=user_id, message_id=msg_id, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        # Первое сообщение
        if photo:
            msg = await bot.send_photo(chat_id=user_id, photo=photo, caption=text, reply_markup=reply_markup)
        else:
            msg = await bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup, parse_mode="Markdown")
        user_main_msg[user_id] = msg.message_id

@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    # Показываем первое фото галереи (если есть)
    if GALLERY_ITEMS:
        first = GALLERY_ITEMS[0]
        text = f"🎞 *THE LAB*\n\n{first['caption']}\n\nВыберите действие:"
        await update_main_message(bot, message.from_user.id, text, reply_markup=gallery_kb(0, len(GALLERY_ITEMS)), photo=first['photo'])
        await state.set_state(GalleryState.viewing)
        await state.update_data(gallery_index=0)
    else:
        await update_main_message(bot, message.from_user.id, WELCOME_TEXT, reply_markup=main_menu_kb)

# ----- Навигация по главным разделам -----
@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    if GALLERY_ITEMS:
        await state.set_state(GalleryState.viewing)
        await state.update_data(gallery_index=0)
        first = GALLERY_ITEMS[0]
        text = f"🎞 *THE LAB*\n\n{first['caption']}\n\nВыберите действие:"
        await update_main_message(bot, callback.from_user.id, text, reply_markup=gallery_kb(0, len(GALLERY_ITEMS)), photo=first['photo'])
    else:
        await update_main_message(bot, callback.from_user.id, WELCOME_TEXT, reply_markup=main_menu_kb)
    await callback.answer()

@router.callback_query(F.data == "main_catalog")
async def show_catalog(callback: CallbackQuery, bot: Bot):
    await update_main_message(bot, callback.from_user.id, "📋 *Каталог плёнок:*", reply_markup=catalog_kb())
    await callback.answer()

@router.callback_query(F.data == "main_cart")
async def show_cart(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await update_main_message(bot, user_id, "🛒 Корзина пуста.", reply_markup=main_menu_kb)
    else:
        text = format_cart(cart)
        await update_main_message(bot, user_id, text, reply_markup=cart_kb(user_id, cart))
    await callback.answer()

@router.callback_query(F.data == "main_orders")
async def show_my_orders(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    orders = get_user_orders(user_id)
    if not orders:
        await update_main_message(bot, user_id, "У вас пока нет заказов.", reply_markup=main_menu_kb)
    else:
        await update_main_message(bot, user_id, "📦 *Ваши заказы:*", reply_markup=my_orders_kb(orders))
    await callback.answer()

@router.callback_query(F.data == "main_faq")
async def show_faq(callback: CallbackQuery, bot: Bot):
    text = (
        "❓ *Часто задаваемые вопросы*\n\n"
        "1. **Как проявлять ECN-2?**\n   Рекомендуем специальный набор.\n"
        "2. **Срок годности?**\n   Хранится в холодильнике до 2 лет.\n"
        "3. **Самовывоз**\n   Станции метро: Курская, Павелецкая, Таганская и др.\n\n"
        "Подробнее спросите у оператора."
    )
    await update_main_message(bot, callback.from_user.id, text, reply_markup=main_menu_kb)
    await callback.answer()

@router.callback_query(F.data == "main_labnotes")
async def show_labnotes(callback: CallbackQuery, bot: Bot):
    text = (
        "📓 *Заметки лаборатории*\n\n"
        "Плёнка Kodak 5207 – легендарный материал. Обеспечивает мягкие тона и широкий динамический диапазон.\n"
        "Для проявки ECN-2 требуется удаление ретуши (rem-jet)."
    )
    await update_main_message(bot, callback.from_user.id, text, reply_markup=main_menu_kb)
    await callback.answer()

# ----- Галерея (карусель) -----
@router.callback_query(GalleryState.viewing, F.data == "gallery_next")
async def gallery_next(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    idx = data.get("gallery_index", 0)
    if idx + 1 < len(GALLERY_ITEMS):
        new_idx = idx + 1
        item = GALLERY_ITEMS[new_idx]
        text = f"🎞 *THE LAB*\n\n{item['caption']}\n\nВыберите действие:"
        await update_main_message(bot, callback.from_user.id, text, reply_markup=gallery_kb(new_idx, len(GALLERY_ITEMS)), photo=item['photo'])
        await state.update_data(gallery_index=new_idx)
    await callback.answer()

@router.callback_query(GalleryState.viewing, F.data == "gallery_prev")
async def gallery_prev(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    idx = data.get("gallery_index", 0)
    if idx - 1 >= 0:
        new_idx = idx - 1
        item = GALLERY_ITEMS[new_idx]
        text = f"🎞 *THE LAB*\n\n{item['caption']}\n\nВыберите действие:"
        await update_main_message(bot, callback.from_user.id, text, reply_markup=gallery_kb(new_idx, len(GALLERY_ITEMS)), photo=item['photo'])
        await state.update_data(gallery_index=new_idx)
    await callback.answer()

# ----- Каталог: выбор товара -----
@router.callback_query(F.data.startswith("product_"))
async def show_product(callback: CallbackQuery, bot: Bot):
    pid = callback.data.split("_")[1]
    product = PRODUCTS.get(pid)
    if not product:
        await callback.answer("Товар не найден")
        return
    text = f"*{product['name']}*\n\n{product['description']}\n\n💰 Цена: {product['price']} {CURRENCY_SYMBOL}"
    await update_main_message(bot, callback.from_user.id, text, reply_markup=product_kb(pid))
    await callback.answer()

@router.callback_query(F.data.startswith("add_"))
async def add_to_cart_handler(callback: CallbackQuery, bot: Bot):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    add_to_cart(user_id, pid, 1)
    await callback.answer(f"✅ {PRODUCTS[pid]['name']} добавлен в корзину", show_alert=True)
    # Остаёмся на карточке товара, но можно показать корзину
    await show_product(callback, bot)

# ----- Корзина: изменение количества -----
@router.callback_query(F.data.startswith("inc_"))
async def increment_quantity(callback: CallbackQuery, bot: Bot):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if pid in cart:
        new_qty = cart[pid] + 1
        set_quantity(user_id, pid, new_qty)
    await show_cart(callback, bot)

@router.callback_query(F.data.startswith("dec_"))
async def decrement_quantity(callback: CallbackQuery, bot: Bot):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if pid in cart and cart[pid] > 1:
        new_qty = cart[pid] - 1
        set_quantity(user_id, pid, new_qty)
    elif pid in cart and cart[pid] == 1:
        remove_from_cart(user_id, pid)
    await show_cart(callback, bot)

@router.callback_query(F.data.startswith("del_"))
async def delete_item(callback: CallbackQuery, bot: Bot):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    remove_from_cart(user_id, pid)
    await show_cart(callback, bot)

@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    clear_cart(user_id)
    await update_main_message(bot, user_id, "🛒 Корзина очищена.", reply_markup=main_menu_kb)
    await callback.answer()

# ----- Оформление заказа -----
@router.callback_query(F.data == "checkout")
async def checkout_start(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await callback.answer("Корзина пуста", show_alert=True)
        return
    await update_main_message(bot, user_id, "📍 Выберите станцию метро для самовывоза:", reply_markup=pickup_stations_kb())
    await state.set_state(OrderState.waiting_for_pickup_station)
    await callback.answer()

@router.callback_query(OrderState.waiting_for_pickup_station, F.data.startswith("station_"))
async def process_pickup_station(callback: CallbackQuery, state: FSMContext, bot: Bot):
    station = callback.data.split("station_", 1)[1]
    await state.update_data(pickup_station=station)
    await update_main_message(bot, callback.from_user.id, "Выберите способ оплаты:", reply_markup=payment_kb())
    await state.set_state(OrderState.waiting_for_payment_method)
    await callback.answer()

@router.callback_query(OrderState.waiting_for_payment_method, F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, state: FSMContext, bot: Bot):
    method_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await update_main_message(bot, user_id, "Корзина пуста.", reply_markup=main_menu_kb)
        await state.clear()
        return

    data = await state.get_data()
    pickup_station = data.get("pickup_station", "Не указана")

    subtotal = sum(PRODUCTS[pid]["price"] * qty for pid, qty in cart.items())
    total = subtotal
    items = [{"id": pid, "qty": qty} for pid, qty in cart.items()]

    order_id = create_order(user_id, items, subtotal, total, method_code, pickup_station)

    await notify_admin_new_order(bot, order_id, user_id, items, subtotal, total, method_code, pickup_station)

    if method_code == "usdt":
        text = (
            f"💰 *Оплата USDT (TRC20)*\n\n"
            f"Сумма: {total} {CURRENCY_SYMBOL}\n"
            f"Кошелёк: `{USDT_WALLET}`\n"
            f"После оплаты нажмите 'Я оплатил'.\n\nЗаказ №{order_id}"
        )
        await update_main_message(bot, user_id, text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"i_paid_{order_id}")]
        ]))
    elif method_code == "card":
        text = (
            f"💳 *Оплата картой*\n\n"
            f"Сумма: {total} {CURRENCY_SYMBOL}\n"
            f"Реквизиты: {CARD_DETAILS}\n"
            f"Заказ №{order_id}\n\nПосле перевода нажмите 'Я оплатил'."
        )
        await update_main_message(bot, user_id, text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"i_paid_{order_id}")]
        ]))
    else:
        text = f"📱 *Ручной перевод*\n\nЗаказ №{order_id} принят. Менеджер свяжется с вами.\nСтанция метро: {pickup_station}"
        await update_main_message(bot, user_id, text, reply_markup=main_menu_kb)
    await state.clear()

@router.callback_query(F.data.startswith("i_paid_"))
async def user_paid(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split("_")[2])
    from config import ADMIN_CHAT_ID
    await bot.send_message(
        ADMIN_CHAT_ID,
        f"💰 Пользователь @{callback.from_user.username} (id:{callback.from_user.id}) сообщил об оплате заказа #{order_id}."
    )
    await update_main_message(bot, callback.from_user.id, "Спасибо, ваш платёж проверяется. Мы свяжемся с вами.", reply_markup=main_menu_kb)
    await callback.answer()

# ----- Детали заказа -----
@router.callback_query(F.data.startswith("order_"))
async def order_detail(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    orders = get_user_orders(user_id)
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        await callback.answer("Заказ не найден")
        return
    items_text = "\n".join([f"{PRODUCTS[i['id']]['name']} x{i['qty']}" for i in order["items"]])
    status_rus = {"pending": "⏳ Ожидает оплаты", "paid": "✅ Оплачен", "shipped": "📦 Отправлен", "completed": "🏁 Завершён"}.get(order["status"], order["status"])
    text = f"*Заказ #{order_id}*\n\n{items_text}\n\nИтого: {order['total']} ₽\nСтатус: {status_rus}\nСамовывоз: {order['pickup_station']}"
    await update_main_message(bot, user_id, text, reply_markup=order_detail_kb(order_id, order.get("tracking_number")))
    await callback.answer()

@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()
