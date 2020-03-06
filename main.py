import os, sys
from flask import Flask, request
from tb0t import start_bot,stop_bot

if 'TELEBOT_TOKEN' not in os.environ or 'VIBER_TOKEN' not in os.environ or 'DATABASE_URL' not in os.environ:
    print('REQUIRED VARIABLES NOT SET (TELEBOT_TOKEN or VIBER_TOKEN or DATABASE_URL)')
    sys.exit()
teletoken=os.environ['TELEBOT_TOKEN']
server = Flask(__name__)

@server.route('/tbot/' + teletoken, methods=['POST'])
def getMessage():
    start_bot(teletoken)
    return "!", 200

@server.route("/tbot/")
def webhook():
    stop_bot(teletoken)
    return "!", 200

if __name__ == '__main__':
    server.debug = True
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8443)), ssl_context=('ssl/eco_crt.crt','ssl/eco_crt.key'))