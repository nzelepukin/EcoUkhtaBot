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
        if event.type == VkEventType.MESSAGE_NEW: #and event.to_me and event.text:
            print('id{}: "{}"'.format(event.user_id, event.text), end=' ')
            '''
            if event.lat and event.long:
                    my_location={'latitude':event.lat,'longitude':event.long}
                    places = select_places() #red_get(str(message.from_user.id)+'_type'))
                    dist={p['id']:distance(my_location['longitude'],my_location['latitude'],p['loc_lon'],p['loc_lat']) for p in places}
                    min_dist=min(dist.keys(), key=(lambda k: dist[k]))
                    db_place = select_place_param(min_dist)
                    photo = upload.photo_messages(photos=db_place['photo'])[0]
                    vk.messages.send(
                        user_id=event.user_id,
                        attachment=[photo],
                        random_id=get_random_id(),
                        lat=db_place['loc_lat'],
                        long=db_place['loc_lon'],
                        message=db_place['info']
                    )
                '''
    return 'ok'
    '''    
            response = session.get(
                'http://api.duckduckgo.com/',
                params={
                    'q': event.text,
                    'format': 'json'
                }
            ).json()

            text = response.get('AbstractText')
            image_url = response.get('Image')

            if not text:
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message='No results'
                )
                print('no results')
                continue

            attachments = []

            if image_url:
                image = session.get(image_url, stream=True)
                photo = upload.photo_messages(photos=image.raw)[0]

                attachments.append(
                    'photo{}_{}'.format(photo['owner_id'], photo['id'])
                )

            vk.messages.send(
                user_id=event.user_id,
                attachment=','.join(attachments),
                random_id=get_random_id(),
                message=text
            )
            print('ok')
    '''

    '''
    # получаем данные из запроса
    try:
        data = request.json
    except: return 'not ok'
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
        print (data)
        from_id = data['object']['user_id']
        # отправляем сообщение
        vk.messages.send(
            message=data['object']['body'],
            random_id=get_random_id(),
            peer_id=from_id
        )
        # возвращаем серверу VK "ok" и код 200
        return 'ok'

    return 'ok'  # игнорируем другие типы
    '''