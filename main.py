import os, sys, ssl
import requests
from flask import Flask, request
from tb0t import update_tbot, start_tbot 
from vb0t import update_vbot, start_vbot
import vk_api
from vk_api.utils import get_random_id

if 'TELEBOT_TOKEN' not in os.environ or 'VIBER_TOKEN' not in os.environ or 'DATABASE_URL' not in os.environ:
    print('REQUIRED VARIABLES NOT SET (TELEBOT_TOKEN or VIBER_TOKEN or DATABASE_URL)')
    sys.exit()
teletoken=os.environ['TELEBOT_TOKEN']
vibertoken=os.environ['VIBER_TOKEN']
server = Flask(__name__)
vk_session = vk_api.VkApi(token=os.environ['VK_TOKEN'])
vk = vk_session.get_api()

confirmation_code = 'ab21b640'

@server.route('/tbot/' + teletoken, methods=['POST'])
def getTMessage():
    update_tbot(teletoken)
    return "!", 200

@server.route("/tbot/")
def Twebhook():
    start_tbot(teletoken)
    return "!", 200

@server.route('/vbot/' + vibertoken, methods=['POST'])
def getVMessage():
    update_tbot(vibertoken)
    return "!", 200

@server.route("/vbot/")
def Vwebhook():
    start_tbot(vibertoken)
    return "!", 200

@server.route('/vkbot/', methods=['POST'])
def verifyVMessage():
    # получаем данные из запроса
    data = request.get_json(force=True, silent=True)
    # ВКонтакте в своих запросах всегда отправляет поле type:
    if not data or 'type' not in data:
        print (data )
        return 'not ok'

    # проверяем тип пришедшего события
    if data['type'] == 'confirmation':
        # если это запрос защитного кода
        # отправляем его
        return confirmation_code
    # если же это сообщение, отвечаем пользователю
    elif data['type'] == 'message_new':
        # получаем ID пользователя
        from_id = data['object']['from_id']
        # отправляем сообщение
        vk.messages.send(
            message=data['object']['body'],
            random_id=get_random_id(),
            peer_id=from_id
        )
        # возвращаем серверу VK "ok" и код 200
        return 'ok'

    return 'ok'  # игнорируем другие типы



if __name__ == '__main__':
    server.debug = True
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8443)))