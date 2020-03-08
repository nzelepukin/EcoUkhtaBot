import vk_api
from vk_api.utils import get_random_id

vk_session = vk_api.VkApi(token=os.environ['VK_TOKEN'])
vk = vk_session.get_api()

confirmation_code = 'ab21b640'
def start_vk():
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
        return ok
    elif data['type'] == 'wall_post_new':
        # получаем ID пользователя
        from_id = data['object']['user_id']
        # отправляем сообщение
        vk.messages.send(
            message=data['object']['text'],
            peer_id=from_id
        )
        # возвращаем серверу VK "ok" и код 200
        return data['object']['body']

    return 'ok'  # игнорируем другие типы