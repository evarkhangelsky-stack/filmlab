from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_CHAT_ID, PRODUCTS, CURRENCY_SYMBOL
from database import update_order_status, get_user_orders

router = Router()

class AdminState(StatesGroup):
    waiting_tracking = State()

async def notify_admin_new_order(bot: Bot, order_id, user_id, items, subtotal, total, payment_method, pickup_station):
    items_text = "\n".join([f"{PRODUCTS[i['id']]['name']} x{i['qty']}" for i in items])
    text = (
        f"🆕 NEW ORDER #{order_id}\n\n"
        f"{items_text}\n"
        f"Total: {total} {CURRENCY_SYMBOL}\n"
        f"Payment: {payment_method}\n"
        f"Pickup: {pickup_station}\n"
        f"User: [id{user_id}](tg://user?id={user_id})"
    )
    await bot.send_message(ADMIN_CHAT_ID, text, parse_mode="Markdown")

@router.callback_query(F.data.startswith("confirm_pay_"))
async def confirm_payment(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    update_order_status(order_id, "paid")
    await callback.message.edit_text(f"✅ Order #{order_id} marked as paid.")
    # Уведомить пользователя
    # (нужно получить user_id из заказа, для простоты опустим)
    await callback.answer()

@router.message(Command("track"))
async def ask_tracking(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_CHAT_ID:
        return
    await message.answer("Send order ID and tracking number in format: ORDER_ID TRACKING_NUMBER")
    await state.set_state(AdminState.waiting_tracking)

@router.message(AdminState.waiting_tracking)
async def set_tracking(message: Message, state: FSMContext):
    try:
        parts = message.text.split()
        order_id = int(parts[0])
        tracking = parts[1]
        update_order_status(order_id, "shipped", tracking)
        await message.answer(f"Tracking {tracking} added to order #{order_id}")
        # Уведомить пользователя
        # (нужно получить user_id)
    except:
        await message.answer("Invalid format. Use: ORDER_ID TRACKING_NUMBER")
    await state.clear()
