import os, sys, ssl
from flask import Flask, request
from tb0t import start_tbot,update_tbot
from vb0t import start_vbot,update_vbot

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

@server.route('/vbot/' + teletoken, methods=['POST'])
def getVMessage():
    update_tbot(vibertoken)
    return "!", 200

@server.route("/vbot/")
def Vwebhook():
    start_tbot(vibertoken)
    return "!", 200

if __name__ == '__main__':
    server.debug = True
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8443)))