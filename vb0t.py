import os,sys,json,viber
from helper import distance
from flask import request,Response
from db import red_set, red_get, insert_user,insert_place,insert_log,select_places,select_place_param,select_userid_by_name
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
from viberbot.api.messages import TextMessage, PictureMessage
from viberbot.api.messages.data_types.location import Location

bot_configuration = BotConfiguration(
	name='EcoUkhtaBot',
	avatar='img/EcoLogo.jpg',
	auth_token=os.environ('VIBER_TOKEN')
)
viber = Api(bot_configuration)
def update_vbot(token):
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data())
    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        # lets echo back
        viber.send_messages(viber_request.sender.id, [
            message
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [
            TextMessage(text="thanks for subscribing!")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request))
    return Response(status=200)

def start_vbot(token):
    viber.unset_webhook()
    viber.set_webhook(url='https://ecoukhta.herokuapp.com/vbot/' + token)