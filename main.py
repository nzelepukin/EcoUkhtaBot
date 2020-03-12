import os, sys, ssl
import requests
from flask import Flask, request
from tb0t import update_tbot, start_tbot 
from vb0t import update_vbot, start_vbot
from vkb0t import start_vk
from db import select_place_param


if 'TELEBOT_TOKEN' not in os.environ or 'VIBER_TOKEN' not in os.environ or 'DATABASE_URL' not in os.environ:
    print('REQUIRED VARIABLES NOT SET (TELEBOT_TOKEN or VIBER_TOKEN or DATABASE_URL)')
    sys.exit()
teletoken=os.environ['TELEBOT_TOKEN']
vibertoken=os.environ['VIBER_TOKEN']
server = Flask(__name__)

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
def VkMessage():
    return start_vk()

@server.route('/images/', methods=['GET'])
def Images():
    try:
        place = str(request.args.get('img'))
    except:
        place = '1'
    db_place = select_place_param(place)
    return db_place['info'], 200

if __name__ == '__main__':
    server.debug = True
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8443)))