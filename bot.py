from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

# إعدادات البوت
API_ID = 28384147  # ضع هنا API ID
API_HASH = "1508ece11802e6214b4138e5917fef4b"  # ضع هنا API Hash
BOT_TOKEN = "7611194546:AAEPJ_xSoDH3sS3112qQoJH78LIV1jgxkkA"  # ضع هنا توكن البوت
OWNER_ID = 7115002714  # ضع هنا آيدي المطور الأساسي

# قوائم التحكم
ADMINS = [OWNER_ID]
BOT_STATUS = True
FORCED_SUBSCRIPTION = None
ENABLE_CONTACT = False

# إنشاء البوت
app = Client("session_extractor", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# رسالة الترحيب مع الأزرار
WELCOME_MESSAGE = "🎉 مرحبًا بك في بوت استخراج الجلسات! استخدم الأزرار أدناه للاستفادة من ميزات البوت."

WELCOME_BUTTONS = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("📥 استخراج الجلسة", callback_data="extract_session")],
        [
            InlineKeyboardButton("📢 قناة السورس", url="https://t.me/source_channel"),
            InlineKeyboardButton("👤 مطور البوت", url="https://t.me/developer_handle"),
        ],
    ]
)

ADMIN_PANEL_BUTTONS = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("✅ تفعيل البوت", callback_data="enable_bot"),
         InlineKeyboardButton("❌ تعطيل البوت", callback_data="disable_bot")],
        [InlineKeyboardButton("📢 تفعيل الاشتراك", callback_data="enable_subscription"),
         InlineKeyboardButton("❌ تعطيل الاشتراك", callback_data="disable_subscription")],
        [InlineKeyboardButton("📩 تفعيل التواصل", callback_data="enable_contact"),
         InlineKeyboardButton("❌ تعطيل التواصل", callback_data="disable_contact")],
        [InlineKeyboardButton("📊 عدد الأعضاء", callback_data="member_count")],
        [InlineKeyboardButton("⬆️ رفع أدمن", callback_data="promote_admin"),
         InlineKeyboardButton("⬇️ تنزيل أدمن", callback_data="demote_admin")],
    ]
)

# رسالة البداية
@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id

    if user_id in ADMINS:
        await message.reply_text(
            "🎉 مرحبًا بك في لوحة تحكم الأدمن!",
            reply_markup=ADMIN_PANEL_BUTTONS,
        )
    else:
        await message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=WELCOME_BUTTONS,
        )

# استخراج الجلسة
@app.on_callback_query(filters.regex("extract_session"))
async def extract_session(client, callback_query):
    user_id = callback_query.from_user.id

    if not BOT_STATUS:
        await callback_query.answer("❌ البوت معطل حاليًا.", show_alert=True)
        return

    await callback_query.message.reply_text("🚀 أرسل الآن رقم الهاتف (مع رمز الدولة):")
    phone_number = await app.ask(user_id, "📱 أدخل رقم الهاتف:")
    try:
        async with Client(":memory:", api_id=API_ID, api_hash=API_HASH) as temp_client:
            code = await app.ask(user_id, "📩 أدخل الكود الذي وصلك الآن:")
            await temp_client.sign_in(phone_number, code)

            # تحقق بخطوتين إذا لزم
            try:
                password = await app.ask(user_id, "🔒 الحساب محمي بكلمة مرور، أدخلها الآن:")
                await temp_client.check_password(password)
            except:
                pass

            session_string = await temp_client.export_session_string()

            # إرسال الجلسة إلى الرسائل المحفوظة
            await temp_client.send_message(
                "me",
                f"🎉 **تم استخراج الجلسة بنجاح:**\n\n`{session_string}`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔗 نسخ الجلسة", callback_data="copy_session")]]
                ),
            )

            await callback_query.message.reply_text(
                "✅ تم استخراج الجلسة بنجاح!\nتم إرسالها إلى رسائلك المحفوظة.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("📥 الرسائل المحفوظة", url="https://t.me/saved_messages")]]
                ),
            )
    except Exception as e:
        await callback_query.message.reply_text(f"❌ حدث خطأ أثناء استخراج الجلسة:\n{e}")

# لوحة تحكم الأدمن
@app.on_callback_query()
async def admin_controls(client, callback_query):
    global BOT_STATUS, FORCED_SUBSCRIPTION, ENABLE_CONTACT

    user_id = callback_query.from_user.id
    if user_id not in ADMINS:
        await callback_query.answer("❌ ليس لديك صلاحيات.", show_alert=True)
        return

    if callback_query.data == "enable_bot":
        BOT_STATUS = True
        await callback_query.answer("✅ تم تفعيل البوت.")
    elif callback_query.data == "disable_bot":
        BOT_STATUS = False
        await callback_query.answer("❌ تم تعطيل البوت.")
    elif callback_query.data == "enable_subscription":
        FORCED_SUBSCRIPTION = await app.ask(user_id, "📢 أرسل معرف القناة:")
        await callback_query.answer("✅ تم تفعيل الاشتراك الإجباري.")
    elif callback_query.data == "disable_subscription":
        FORCED_SUBSCRIPTION = None
        await callback_query.answer("❌ تم تعطيل الاشتراك الإجباري.")
    elif callback_query.data == "enable_contact":
        ENABLE_CONTACT = True
        await callback_query.answer("✅ تم تفعيل التواصل.")
    elif callback_query.data == "disable_contact":
        ENABLE_CONTACT = False
        await callback_query.answer("❌ تم تعطيل التواصل.")
    elif callback_query.data == "member_count":
        members = len(await app.get_users())
        await callback_query.message.reply_text(f"📊 عدد الأعضاء في البوت: {members}")
    elif callback_query.data == "promote_admin":
        new_admin = await app.ask(user_id, "👤 أرسل معرف المستخدم لرفعه أدمن:")
        ADMINS.append(int(new_admin))
        await callback_query.answer(f"✅ تم رفع {new_admin} كأدمن.")
    elif callback_query.data == "demote_admin":
        remove_admin = await app.ask(user_id, "👤 أرسل معرف المستخدم لإزالته من الأدمن:")
        ADMINS.remove(int(remove_admin))
        await callback_query.answer(f"❌ تم إزالة {remove_admin} من الأدمن.")

# تشغيل البوت
app.run()
# انشاء المبرمج فيكتور
# المبرمج فيكتور @div_victor
