from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext, \
    CallbackQueryHandler
from telegram.constants import ParseMode
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import requests


TELEGRAM_TOKEN = '7001434115:AAGkomaoF6-hCGAm18AeD4ZwiGrt8dhCOqc'


ADMINS = [1278109787]

DATE = range(1)


def create_calendar_message(step: str) -> str:
    if step == 'year':
        return "سال مورد نظر را انتخاب کنید 📅"
    elif step == 'month':
        return "ماه مورد نظر را انتخاب کنید 📅"
    elif step == 'day':
        return "روز مورد نظر را انتخاب کنید 📅"


async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id

    if user_id in ADMINS:
        await update.message.reply_text(
            '👋 به بات مدیریت خوش آمدید!\n\nلطفاً تاریخ را انتخاب کنید:',
            parse_mode=ParseMode.HTML,
        )
        calendar, step = DetailedTelegramCalendar().build()
        await update.message.reply_text(
            create_calendar_message(LSTEP[step]),
            reply_markup=calendar
        )
        return DATE
    else:
        await update.message.reply_text('شما مجاز به استفاده از این ربات نیستید.')
        return ConversationHandler.END


async def button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'select_date':
        calendar, step = DetailedTelegramCalendar().build()
        await query.edit_message_text(
            create_calendar_message(LSTEP[step]),
            reply_markup=calendar
        )
        return DATE


async def get_date(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    result, key, step = DetailedTelegramCalendar().process(query.data)

    if not result and key:
        await query.edit_message_text(
            create_calendar_message(LSTEP[step]),
            reply_markup=key
        )
    elif result:
        await query.edit_message_text(f"تاریخ انتخابی: {result}")
        date = result.strftime('%Y-%m-%d')
        url = f'http://localhost:8000/api/cip/export-pdf/8ba32987-d682-4d49-b054-ac3372fabec6/?date={date}'

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            with open('flight_report.pdf', 'wb') as f:
                f.write(response.content)
            with open('flight_report.pdf', 'rb') as f:
                await query.message.reply_document(f, filename='flight_report.pdf')
        except requests.RequestException as e:
            await query.message.reply_text(f'خطا در دریافت PDF: {str(e)}')
        except Exception as e:
            await query.message.reply_text(f'یک خطا رخ داد: {str(e)}')

        return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('عملیات لغو شد.')
    return ConversationHandler.END


async def handle_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'start':
        await query.edit_message_text(
            '👋 به بات مدیریت خوش آمدید!\n\nلطفاً تاریخ را انتخاب کنید:',
            parse_mode=ParseMode.HTML,
        )
        calendar, step = DetailedTelegramCalendar().build()
        await query.message.reply_text(
            create_calendar_message(LSTEP[step]),
            reply_markup=calendar
        )
        return DATE


def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DATE: [CallbackQueryHandler(get_date)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling()


if __name__ == '__main__':
    main()
