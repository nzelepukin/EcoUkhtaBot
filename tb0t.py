import os,telebot,sys,json,time,redis
from helper import distance
from db import red_set, red_get, insert_user,insert_place,insert_log,select_places,select_place_param,select_userid_by_name

teletoken=os.environ['TELEBOT_TOKEN']
keyboard1=telebot.types.ReplyKeyboardMarkup(True,True)
keyboard1.row('battery')
adminkeyboard=telebot.types.ReplyKeyboardMarkup(True,True)
keyboard1.row('del user','del place')
bot = telebot.TeleBot(teletoken)


@bot.message_handler(commands=['start'])
def start_message(message):
    greeting='''
    Привет, скинь геопозицию и бот покажет ближайшую точку сдачи батареек.
    Хочешь увидеть все точки введи /list 
    '''
    bot.send_message(message.chat.id,greeting)


@bot.message_handler(commands=['list'])
def list_message(message):
    places= select_places() #red_get(str(message.from_user.id)+'_type'))
    for p in places:
        db_place = select_place_param(p['id'])
        bot.send_location(message.chat.id, db_place['loc_lat'], db_place['loc_lon'])
        bot.send_photo(message.chat.id, db_place['photo'],caption=db_place['info'])

@bot.message_handler(content_types=['location'])
def list_message(message):
    my_location={'latitude':message.location.latitude,'longitude':message.location.longitude}
    places = select_places() #red_get(str(message.from_user.id)+'_type'))
    dist={p['id']:distance(my_location['longitude'],my_location['latitude'],p['loc_lon'],p['loc_lat']) for p in places}
    min_dist=min(dist.keys(), key=(lambda k: dist[k]))
    db_place = select_place_param(min_dist)
    bot.send_location(message.chat.id, db_place['loc_lat'], db_place['loc_lon'])
    bot.send_photo(message.chat.id, db_place['photo'],caption=db_place['info'])
    insert_log(select_userid_by_name(str(message.from_user.id)),db_place['id'])

@bot.message_handler(commands=['add'])
def add_message(message):
    bot.send_message(message.chat.id,'Привет, что сдаем?',reply_markup=keyboard1)
    insert_user(message)
    bot.register_next_step_handler(message, get_type)

def get_type(message):
    user=str(message.from_user.id)
    red_set(user+'_type',message.text)
    bot.send_message(message.chat.id,'Введи геолокацию.')
    bot.register_next_step_handler(message, get_location)     

def get_location(message):
    user=str(message.from_user.id)
    red_set(user+'_lat',message.location.latitude)
    red_set(user+'_lon',message.location.longitude)
    bot.send_message(message.chat.id,'Введи назваие и режим работы пункта.')
    bot.register_next_step_handler(message, get_info)

def get_info(message):
    user=str(message.from_user.id)
    red_set(user+'_info',message.text)
    bot.send_message(message.chat.id,'Вставьте фото.')
    bot.register_next_step_handler(message, get_photo)

def get_photo(message):
    file_info = bot.get_file(message.photo[0].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    insert_place(message,downloaded_file)
    bot.send_message(message.chat.id,'Спасибо за информацию! Пункт добавлен') 

def start_bot(token):
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])

def stop_bot(token):
    bot.remove_webhook(certificate=open('ssl/eco_crt.crt', 'r'))
    bot.set_webhook(url='https://ecoukhta.herokuapp.com/' + token,certificate=open('ssl/eco_crt.crt', 'r'))
