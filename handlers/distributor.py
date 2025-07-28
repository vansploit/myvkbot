import json
from .keyboards import kb
from vk_api.utils import get_random_id


class Message:
    
    def __init__(self, vk, msg):
        self.vk = vk
        self.state_storage = {}

            
    def __commands_handler__(self):
        
        payload = json.loads(payload)
            
        print(payload)    
            
        match payload.get("command"):
            case "start":
                text = "Стартовое меню:"
                keyboard = kb["start"]
                
            case "create_request":
                text = "Кем вы хотите быть?"
                keyboard = kb["user_request"]
                self.__set_state__(user_id, RequsetState.writename)

            case "info":
                text = "Кнопка еще не готова!"
                
                
    def __send_message__(self):
        print(f"user_id: " + str(self.user_id) + "\nmessage: " + self.text + "\nkeyboard" + str(self.keyboard))
        self.vk.messages.send(
            user_id = self.user_id,
            message = self.text,
            keyboard = self.keyboard,
            random_id = get_random_id()
            )


    def handling_message(self, msg):
        user_id = msg.from_id