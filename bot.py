from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# دالة لإرسال الرد على أمر /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('أهلاً! كيف يمكنني مساعدتك؟')

# دالة للرد على الرسائل
def reply_to_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()
    if 'مرحبا' in user_message:
        update.message.reply_text('أهلاً وسهلاً!')
    else:
        update.message.reply_text('عذرًا، لم أفهم رسالتك.')

def main():
    # أدخل هنا التوكن الخاص بك
    TELEGRAM_TOKEN = '7610862594:AAFn4nk-4taH0pswZwjbk6j9GS_WHrGA-6g'
    
    # إعداد البوت
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # إضافة معالجات الأوامر
    dispatcher.add_handler(CommandHandler("start", start))

    # إضافة معالج للرد على الرسائل
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_to_message))

    # بدء البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()