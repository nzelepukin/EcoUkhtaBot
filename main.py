import os, sys, ssl
import requests
from flask import Flask, request, send_file
from tb0t import update_tbot, start_tbot 
from vkb0t import start_vk
from db import select_place_param

if 'TELEBOT_TOKEN' not in os.environ or 'VK_TOKEN' not in os.environ or 'DATABASE_URL' not in os.environ:
    print('REQUIRED VARIABLES NOT SET (TELEBOT_TOKEN or VK_TOKEN or DATABASE_URL)')
    sys.exit()
teletoken=os.environ['TELEBOT_TOKEN']
server = Flask(__name__)

@server.route('/tbot/' + teletoken, methods=['POST'])
def getTMessage():
    update_tbot(teletoken)
    return "!", 200

@server.route("/tbot/")
def Twebhook():
    start_tbot(teletoken)
    return "!", 200

@server.route('/vkbot/', methods=['POST'])
def VkMessage():
    return start_vk()

@server.route('/images/', methods=['GET'])
def Images():
    if request.args.get('img'): place = str(request.args.get('img'))
    else: place = '1'
    db_place = select_place_param(place)
    with open(place+ '.jpg', 'wb') as new_file:
        new_file.write(db_place['photo'])
    return send_file(place+'.jpg', mimetype='image/jpg')

if __name__ == '__main__':
    server.debug = True
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8443)))