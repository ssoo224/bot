from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.storage import InMemoryStorage  # التخزين المؤقت

# إعدادات البوت
API_ID = 28384147  # ضع هنا API ID
API_HASH = "1508ece11802e6214b4138e5917fef4b"  # ضع هنا API Hash
BOT_TOKEN = "7611194546:AAEPJ_xSoDH3sS3112qQoJH78LIV1jgxkkA"  # ضع هنا توكن البوت

# إنشاء البوت
storage = InMemoryStorage()  # استخدام التخزين المؤقت
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
        if "phone_number" not in storage:
            storage[user_id] = {"phone_number": text}
            await message.reply_text("📩 أدخل الآن كود التحقق الذي وصلك:")
            return

        # الخطوة 2: جمع كود التحقق
        if "code" not in storage[user_id]:
            storage[user_id]["code"] = text
            phone_number = storage[user_id]["phone_number"]

            async with Client(":memory:", api_id=API_ID, api_hash=API_HASH) as temp_client:
                try:
                    await temp_client.sign_in(phone_number, storage[user_id]["code"])

                    # إذا كان الحساب محميًا بكلمة مرور
                    if "password" not in storage[user_id]:
                        await message.reply_text("🔒 الحساب محمي بكلمة مرور. أدخلها الآن:")
                        return

                    password = storage[user_id]["password"]
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
        elif "password" not in storage[user_id]:
            storage[user_id]["password"] = text

    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ: {e}")


# تشغيل البوت
app.run()
