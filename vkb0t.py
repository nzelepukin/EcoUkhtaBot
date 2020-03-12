import vk_api, os
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from flask import request
from helper import distance
from db import red_set, red_get, insert_user,insert_place,insert_log,select_places,select_place_param,select_userid_by_name

vk_session = vk_api.VkApi(token=os.environ['VK_TOKEN'])
vk = vk_session.get_api()

confirmation_code = 'ab21b640'

upload = VkUpload(vk_session)  # Для загрузки изображений
longpoll = VkLongPoll(vk_session)

def start_vk():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
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
                #photo = upload.photo_messages(photos=db_place['photo'])[0]
                vk.messages.send(
                    user_id=event.user_id,
                    #attachment=[photo],
                    random_id=get_random_id(),
                    lat=db_place['loc_lat'],
                    long=db_place['loc_lon'],
                    message=db_place['info']
                )
            return 'ok'
        else: return 'ok'

