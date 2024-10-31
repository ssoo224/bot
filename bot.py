import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot("7533541751:AAHS7A80PdLVOIypjBqw5wYw0z68sUVi7EE")

@bot.message_handler(commands=['start'])
def n4(message):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("🔗", url="https://t.me/rr8r9")  
    markup.add(btn)   
    msg = bot.send_message(
        message.chat.id, 
        "- أهلاً بك عزيزي في بوت فحص يوزرات الأنستا المتاحة \n- أرسل اليوزر بدون @", 
        reply_markup=markup
    )
    
    bot.register_next_step_handler(msg, userins)

def userins(message):
    user = message.text
    url = requests.post(
        'https://www.instagram.com/accounts/web_create_ajax/attempt/',
        headers={
            'Host': 'www.instagram.com',
            'content-length': '85',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101"',
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': '0',
            'sec-ch-ua-mobile': '?0',
            'x-instagram-ajax': '81f3a3c9dfe2',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'x-requested-with': 'XMLHttpRequest',
            'x-asbd-id': '198387',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Safari/537.36',
            'x-csrftoken': 'jzhjt4G11O37lW1aDFyFmy1K0yIEN9Qv',
            'sec-ch-ua-platform': '"Linux"',
            'origin': 'https://www.instagram.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.instagram.com/accounts/emailsignup/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-IQ,en;q=0.9',
            'cookie': 'csrftoken=jzhjt4G11O37lW1aDFyFmy1K0yIEN9Qv; mid=YtsQ1gABAAEszHB5wT9VqccwQIUL; ig_did=227CCCC2-3675-4A04-8DA5-BA3195B46425; ig_nrcb=1'
        },
        data=f'email=aakmnnsjskksmsnsn%40gmail.com&username={user}&first_name=&opt_into_one_tap=false'
    )

    if 'feedback_required' in url.text:
        bot.send_message(message.chat.id, "هناك خطأ أثناء الفحص، حاول لاحقًا.")
    elif '"username_is_taken"' in url.text or '"errors": {"username":' in url.text:
        bot.send_message(message.chat.id, f"اليوزر `{user}` غير متاح ❌", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"اليوزر `{user}` متاح ✅", parse_mode="Markdown")    
    bot.register_next_step_handler(message, userins)


bot.infinity_polling()
