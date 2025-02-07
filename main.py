import telebot
import threading
import requests
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# إعدادات البوت
BOT_TOKEN = "7774589265:AAHIrj_y7dbiBviLkIPqOBFiBtQoMrneXug"  # استبدل بـالتوكن الخاص بك
bot = telebot.TeleBot(BOT_TOKEN)

# تخزين البيانات
urls = []  # قائمة الروابط
lock = threading.Lock()  # قفل لحماية البيانات المشتركة

# بدء نظام Keep-Alive
def keep_alive():
    while True:
        with lock:
            for url in urls:
                try:
                    response = requests.get(url, timeout=5)
                    print(f"Keep-alive successful for {url}, Status: {response.status_code}")
                except Exception as e:
                    print(f"Error keeping {url} alive: {e}")
        time.sleep(120)  # تكرار العملية كل دقيقتين

# بدء نظام Keep-Alive في خيط منفصل
keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()

# لوحة التحكم الرئيسية
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ إضافة رابط", callback_data="add_url"),
        InlineKeyboardButton("📋 إدارة الروابط", callback_data="manage_urls")
    )
    return markup

# لوحة إدارة الروابط
def manage_urls_menu(chat_id, message_id):
    markup = InlineKeyboardMarkup(row_width=2)
    with lock:
        if not urls:
            # عرض النص كنص عادي بدلاً من زر
            bot.send_message(
                chat_id=chat_id,
                text="*لا توجد روابط مضافة*",
                parse_mode='Markdown'
            )
            return
        else:
            for i, url in enumerate(urls):
                markup.add(InlineKeyboardButton(f"🔗 {url[:30]}...", callback_data=f"manage_{i}"))
    markup.add(InlineKeyboardButton("⬅️ العودة", callback_data="main_menu"))
    bot.edit_message_text(
        "*✎┊‌ اختر الرابط لإدارته:*",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

# لوحة تحكم الرابط
def url_control_menu(index):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_{index}"),
        InlineKeyboardButton("⬅️ العودة", callback_data="manage_urls")
    )
    return markup

# الأمر /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "*✨ أهلاً بك في البوت الخاص بإدارة روابطك!*\n\n"
        "*⬇️ اختر من الأزرار التي تظهر لك. 😎*\n\n",
        reply_markup=main_menu(),
        parse_mode='Markdown'  # استخدام Markdown لجعل النص غامق
    )

# التعامل مع أزرار التحكم
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "add_url":
        bot.send_message(
            call.message.chat.id,
            "*✎┊‌ أرسل الرابط الذي تريد إضافته.*",
            parse_mode='Markdown'  # إضافة parse_mode لجعل النص غامق
        )
        bot.register_next_step_handler(call.message, process_add_url)
    elif call.data == "manage_urls":
        manage_urls_menu(call.message.chat.id, call.message.message_id)
    elif call.data.startswith("manage_"):
        index = int(call.data.split("_")[1])
        bot.edit_message_text(
            f"*إدارة الرابط: {urls[index]}*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=url_control_menu(index),
            parse_mode='Markdown'  # إضافة parse_mode لجعل النص غامق
        )
    elif call.data.startswith("delete_"):
        index = int(call.data.split("_")[1])
        with lock:
            url = urls.pop(index)
        bot.answer_callback_query(call.id, f"*تم حذف الرابط: {url}.*", parse_mode='Markdown')
        manage_urls_menu(call.message.chat.id, call.message.message_id)
    elif call.data == "main_menu":
        bot.edit_message_text(
            "*مرحباً! اختر أحد الخيارات أدناه:*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu(),
            parse_mode='Markdown'  # إضافة parse_mode لجعل النص غامق
        )

# إضافة رابط جديد
def process_add_url(message):
    try:
        url = message.text.strip()
        with lock:
            if url in urls:
                bot.send_message(message.chat.id, f"*❌ الرابط {url} موجود بالفعل!*", parse_mode='Markdown')
                return

            # إضافة الرابط
            urls.append(url)
            bot.send_message(
                message.chat.id,
                f"*✅ تم إضافة الرابط بنجاح: {url}*",
                reply_markup=main_menu(),
                parse_mode='Markdown'  # إضافة parse_mode لجعل النص غامق
            )
    except Exception as e:
        bot.send_message(message.chat.id, f"*❌ حدث خطأ: {e}*", parse_mode='Markdown')

# بدء البوت
print("البوت يعمل...")
bot.infinity_polling()
