import os
import json
import telebot
import requests

TOKEN = '00000' # توكن البوت
ADMIN_ID = '000' #  هنا تحط ايدي المشرف عشان تطلع له الاحصائيات فقط يمكنك تطوير البوت اكثر واكثر للتحكم في الاعضاء

bot = telebot.TeleBot(TOKEN)

def save_user(user_id):
    if not os.path.isfile('users.json'):   
        with open('users.json', 'w') as f: 
            json.dump([user_id], f)
    else:
        with open('users.json', 'r+') as f: 
            users = json.load(f)
            if user_id not in users: 
                users.append(user_id)  
                f.seek(0)  
                json.dump(users, f) 

def get_users():
    if os.path.isfile('users.json'):  
        with open('users.json', 'r') as f:  
            return json.load(f)
    else:
        return []  

def get_ayahs(page):
    response = requests.get(f"http://api.alquran.cloud/v1/page/{page}/quran-uthmani") # هذا اتصال API في موقع Alquran Cloud 
    data = json.loads(response.text)
    ayahs = data['data']['ayahs']
    return '\n'.join([f"{ayah['text']} ﴿{ayah['numberInSurah']}﴾" for ayah in ayahs])

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    save_user(user_id)
    bot.send_message(
        user_id,
        "مرحبا ، اقرأ القران من خلال بوت القران الكريم",
        reply_markup=telebot.types.InlineKeyboardMarkup([
            [telebot.types.InlineKeyboardButton(text="بدء القراءة", callback_data="1")]
        ])
    )
    if str(user_id) == ADMIN_ID:  
        bot.send_message(user_id, f'مرحبا مشرف البوت هذا هو عدد مستخدمين البوت: {len(get_users())}')

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    page = int(call.data)
    page = min(604, max(1, page)) # إحصائية الصفحة بين 1 و 604
    text = get_ayahs(page)
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup([
            [telebot.types.InlineKeyboardButton(text=f"الصفحة رقم ﴿{page}﴾", callback_data=str(page))],
            [telebot.types.InlineKeyboardButton(text="الصفحة السابقة", callback_data=str(page - 1)), 
             telebot.types.InlineKeyboardButton(text="الصفحة التالية", callback_data=str(page + 1))]
        ])
    )

bot.polling(none_stop=True)
