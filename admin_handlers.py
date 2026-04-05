from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from config import ADMIN_CHAT_ID, PRODUCTS, CURRENCY_SYMBOL
from database import update_order_status

router = Router()

# Добавляем параметр bot
async def notify_admin_new_order(bot: Bot, order_id, user_id, items, subtotal, total, payment_method, pickup_station):
    items_text = "\n".join([f"{PRODUCTS[i['id']]['name']} x{i['qty']}" for i in items])
    text = (
        f"🆕 *Новый заказ #{order_id}*\n\n"
        f"{items_text}\n"
        f"Сумма: {subtotal} {CURRENCY_SYMBOL}\n"
        f"*Итого: {total} {CURRENCY_SYMBOL}*\n"
        f"Способ оплаты: {payment_method}\n"
        f"Самовывоз: {pickup_station}\n"
        f"Пользователь: [id{user_id}](tg://user?id={user_id})"
    )
    await bot.send_message(ADMIN_CHAT_ID, text, parse_mode="Markdown")

@router.callback_query(F.data.startswith("confirm_pay_"))
async def confirm_payment(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    update_order_status(order_id, "paid")
    await callback.message.edit_text(f"✅ Заказ #{order_id} отмечен как оплаченный.")
    await callback.answer()

@router.callback_query(F.data.startswith("ship_"))
async def ask_tracking(callback: CallbackQuery):
    await callback.answer("Функция в разработке", show_alert=True)
