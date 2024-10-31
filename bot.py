import telebot
import requests
from bs4 import BeautifulSoup
import time
import os

bot = telebot.TeleBot("7681621766:AAFoqsgn1s88fx8Fb6DtXDexO5oyPA533Ac")

def fetch_proxies():
    url = 'https://t.me/s/ProxyMTProto'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    proxies = []
    for message in soup.find_all('a', href=True):
        if 'proxy' in message['href']:
            proxies.append(message['href'])
    
    return proxies

def get_ping(proxy_url):
    try:
        proxy_info = proxy_url.split("://")[1]
        proxy_ip = proxy_info.split(":")[0]
        start_time = time.time()
        response = os.system(f"ping -c 1 {proxy_ip}")
        end_time = time.time()
        if response == 0:
            ping = int((end_time - start_time) * 1000)
            return ping
        else:
            return None
    except Exception as e:
        print(f"Error fetching ping: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    button_get_proxy = telebot.types.InlineKeyboardButton(text="🫧 بروكسي", callback_data="get_proxy")
    markup.add(button_get_proxy)
    bot.send_message(message.chat.id, "- مرحبًا أضغط على زر بروكسيات للبحث عن بروكسي قوي وسريع 🎉 .", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "get_proxy")
def send_proxy(call):
    proxies = fetch_proxies()
    if proxies:
        proxy = proxies[0]
        ping = get_ping(proxy)

        if ping is not None:
            markup = telebot.types.InlineKeyboardMarkup()
            button_connect_proxy = telebot.types.InlineKeyboardButton(text="🔗 اتصال بالبروكسي", url=proxy)
            button_search_stronger = telebot.types.InlineKeyboardButton(text="🔄 البحث عن أقوى", callback_data="search_stronger")
            markup.add(button_connect_proxy, button_search_stronger)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  text=f"- تم الحصول على بروكسي والبنك هو {ping} ms .\n- هل تريد الإتصال ام البحث عن بروكسي اقوى ؟", 
                                  reply_markup=markup)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  text="عذرًا، لم أتمكن من حساب البنك للبروكسي.")
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text="عذرًا، لم يتم العثور على بروكسيات في الوقت الحالي.")
                              

@bot.callback_query_handler(func=lambda call: call.data == "search_stronger")
def search_stronger_proxy(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text="جارٍ البحث عن بروكسي أقوى ...")

    proxies = fetch_proxies()
    if proxies:
        best_proxy = None
        best_ping = float('inf')

        for proxy in proxies:
            ping = get_ping(proxy)
            if ping is not None and ping < best_ping:
                best_ping = ping
                best_proxy = proxy
        
        if best_proxy:
            markup = telebot.types.InlineKeyboardMarkup()
            button_connect_proxy = telebot.types.InlineKeyboardButton(text="🔗 اتصال بالبروكسي", url=best_proxy)
            button_search_stronger = telebot.types.InlineKeyboardButton(text="🔄 البحث عن أقوى", callback_data="search_stronger")
            markup.add(button_connect_proxy, button_search_stronger)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  text=f"- تم العثور على أقوى بروكسي والبنك هو {best_ping} ms.\n- هل تريد الإتصال ام البحث عن بروكسي اقوى ؟", 
                                  reply_markup=markup)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  text="عذرًا، لم أتمكن من العثور على بروكسيات قوية.")
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text="عذرًا، لم يتم العثور على بروكسيات في الوقت الحالي.")

bot.infinity_polling()
