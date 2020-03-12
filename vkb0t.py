import vk_api, os
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from flask import request
from helper import distance
from requests import Session
from db import red_set, red_get, insert_user,insert_place,insert_log,select_places,select_place_param,select_userid_by_name

vk_session = vk_api.VkApi(token=os.environ['VK_TOKEN'])
vk = vk_session.get_api()
session=Session()
confirmation_code = os.environ['VK_CONFIRM_CODE']

upload = VkUpload(vk_session)  # Для загрузки изображений
longpoll = VkLongPoll(vk_session)

def start_vk():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_info={'username':event.user_id, 'messanger':'vk'}
            user_res=vk_session.method("users.getById",{'user_ids':[user_info['username']],'fields':['id','first_name','last_name']})
            print(user_res['items'])
            result = vk_session.method("messages.getById", {"message_ids": [event.message_id],"group_id": 192738048})
            if result['items'][0]['geo']:
                geo = result['items'][0]['geo']['coordinates']
                latitude, longitude = geo['latitude'], geo['longitude']
                print(latitude, longitude)
                my_location={'latitude':latitude,'longitude':longitude}
                places = select_places()
                dist={p['id']:distance(my_location['longitude'],my_location['latitude'],p['loc_lon'],p['loc_lat']) for p in places}
                min_dist=min(dist.keys(), key=(lambda k: dist[k]))
                db_place = select_place_param(min_dist)
                image_url = 'https://ecoukhta.herokuapp.com/images/?img='+str(db_place['id'])
                image = session.get(image_url, stream=True)
                photo = upload.photo_messages(photos=image.raw)[0]
                attachments='photo{}_{}'.format(photo['owner_id'], photo['id'])
                vk.messages.send(
                    user_id=event.user_id,
                    attachment=attachments,
                    random_id=get_random_id(),
                    lat=db_place['loc_lat'],
                    long=db_place['loc_lon'],
                    message=db_place['info']
                )
            return 'ok'
        else: return 'ok'

