import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from config import TOKEN, GROUP_ID
from handlers import distributor


def main():

    try:
        vk_session = vk_api.VkApi(token=TOKEN)
        vk = vk_session.get_api()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    # Если используете LongPoll (для бота)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    
    for event in longpoll.listen():
        print(event.type)
        if event.type == VkBotEventType.MESSAGE_NEW:
            distributor.Message(vk, event.message)
            

if __name__ == '__main__':
    main()