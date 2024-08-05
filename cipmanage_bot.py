from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import requests
import json

# توکن بات تلگرام که از BotFather دریافت کرده‌اید
TELEGRAM_TOKEN = '7318427598:AAFvFxGCnwsaOlWzmQVKFljOg1VS13OuVp8'

# لیست شناسه‌های کاربری مجاز (ID تلگرام)
ADMINS = [1278109787]  # شناسه‌های کاربری مجاز را اینجا وارد کنید

# URL برای دریافت رزروهای در حالت pending
PENDING_RESERVATIONS_URL = 'http://localhost:8000/api/cip/reservations/pending/'


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in ADMINS:
        await update.message.reply_text(
            '👋 **سلام! به بات مدیریت خوش آمدید.**\n\n'
            '🔄 در حال بارگذاری رزروهای جدید...'
        )

        try:
            response = requests.get(PENDING_RESERVATIONS_URL)
            reservations = response.json()

            if not reservations:
                await update.message.reply_text('✅ هیچ رزوری در حالت pending وجود ندارد.')
                return

            for reservation in reservations:
                user = reservation['user']
                cip_id = reservation['cip_id']
                keyboard = [
                    [
                        InlineKeyboardButton("✅ تایید", callback_data=f'approve_{reservation["id"]}'),
                        InlineKeyboardButton("❌ رد", callback_data=f'reject_{reservation["id"]}'),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                message = (
                    f"📋 جزئیات رزرو:\n\n"
                    f"👤 کاربر: {user['username']}\n"
                    f"📧 ایمیل: {user['email']}\n"
                    f"🔢 کد CIP: {cip_id}\n"
                    f"🚎 نام کاروان: {user['convoyName']}\n"
                    f"📞 شماره تلفن: {user['phoneNumber']}\n"
                    f"👫 تعداد بزرگسالان: {reservation['adults']}\n"
                    f"👶 تعداد نوزادان: {reservation['infants']}\n"
                    f"💵 قیمت کلی: {float(reservation['total_price']):,.0f}"
                )
                await update.message.reply_text(message, reply_markup=reply_markup)

        except requests.RequestException as e:
            await update.message.reply_text(f'❗ خطا در دریافت رزروها: {str(e)}')
    else:
        await update.message.reply_text('🚫 شما مجاز به استفاده از این ربات نیستید.')


async def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data = query.data.split('_')
    action = query_data[0]
    reservation_id = query_data[1]

    if action == 'approve':
        url = f'http://localhost:8000/api/cip/reservations/{reservation_id}/approve/'
        try:
            response = requests.post(url)
            response.raise_for_status()
            await query.edit_message_text('✅ رزرو تایید شد.')
        except requests.RequestException as e:
            await query.edit_message_text(f'❗ خطا در تایید رزرو: {str(e)}')

    elif action == 'reject':
        url = f'http://localhost:8000/api/cip/reservations/{reservation_id}/reject/'
        try:
            response = requests.post(url)
            response.raise_for_status()
            await query.edit_message_text('❌ رزرو رد شد.')
        except requests.RequestException as e:
            await query.edit_message_text(f'❗ خطا در رد رزرو: {str(e)}')


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling()


if __name__ == '__main__':
    main()
