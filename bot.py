from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.storage import FileStorage
import os

# إعدادات البوت
API_ID = os.getenv("API_ID")  # تأكد من إضافة API_ID كمتغير بيئي
API_HASH = os.getenv("API_HASH")  # تأكد من إضافة API_HASH كمتغير بيئي
BOT_TOKEN = os.getenv("BOT_TOKEN")  # تأكد من إضافة BOT_TOKEN كمتغير بيئي

# تحديد مجلد العمل في RAILWAY
storage_path = "/app/storage.json"  # استخدم هذا المسار في RAILWAY

# إنشاء التخزين
storage = FileStorage(storage_path)

# إنشاء البوت
app = Client("session_extractor", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, storage=storage)

# رسالة البداية
WELCOME_MESSAGE = "🎉 مرحبًا! أرسل رقم الهاتف لبدء استخراج الجلسة."
WELCOME_BUTTONS = InlineKeyboardMarkup(
    [[InlineKeyboardButton("📢 قناة السورس", url="https://t.me/source_channel")]]
)


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(WELCOME_MESSAGE, reply_markup=WELCOME_BUTTONS)


@app.on_message(filters.private & ~filters.command("start"))
async def handle_messages(client, message):
    try:
        user_id = message.from_user.id
        text = message.text

        # الخطوة 1: جمع رقم الهاتف
        if "phone_number" not in client.storage:
            client.storage[user_id] = {"phone_number": text}
            await message.reply_text("📩 أدخل الآن كود التحقق الذي وصلك:")
            return

        # الخطوة 2: جمع كود التحقق
        if "code" not in client.storage[user_id]:
            client.storage[user_id]["code"] = text
            phone_number = client.storage[user_id]["phone_number"]

            async with Client(":memory:", api_id=API_ID, api_hash=API_HASH) as temp_client:
                try:
                    await temp_client.sign_in(phone_number, client.storage[user_id]["code"])

                    # إذا كان الحساب محميًا بكلمة مرور
                    if "password" not in client.storage[user_id]:
                        await message.reply_text("🔒 الحساب محمي بكلمة مرور. أدخلها الآن:")
                        return

                    password = client.storage[user_id]["password"]
                    await temp_client.check_password(password)

                    # استخراج الجلسة
                    session_string = await temp_client.export_session_string()
                    await temp_client.send_message(
                        "me", f"🎉 **تم استخراج الجلسة بنجاح:**\n\n`{session_string}`"
                    )
                    await message.reply_text(
                        "✅ تم استخراج الجلسة بنجاح! تم إرسالها إلى رسائلك المحفوظة."
                    )
                except Exception as e:
                    await message.reply_text(f"❌ حدث خطأ أثناء العملية:\n{e}")

        # الخطوة 3: جمع كلمة المرور (إذا لزم)
        elif "password" not in client.storage[user_id]:
            client.storage[user_id]["password"] = text

    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ: {e}")


# تشغيل البوت
app.run()
