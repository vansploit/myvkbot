import os
import importlib
import inspect
import logging
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from typing import List
from .router import Router
from .fsm import FSM
from .message import VkMessage
from utils.events import dict_to_obj
from db import UserDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = UserDatabase()

class VkBotDispatcher:
    def __init__(self, group_id: int, token: str):
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id=group_id)
        self.routers: List[Router] = []
        self.fsm = FSM()
        self.db = db

    def include_routers_from_folder(self, directory):
    
        # Получаем список файлов в директории
        for file in os.listdir(directory):
            if file.endswith('.py') and not file.startswith('__'):
                module_name = file[:-3]  # Убираем .py
                
                try:
                    # Импортируем модуль
                    module = importlib.import_module(f"{directory}.{module_name}")
                    
                    # Проверяем наличие переменной var в модуле
                    if hasattr(module, 'router'):
                        self.include_router(module.router)
                except ImportError as e:
                    print(f"Ошибка при импорте модуля {module_name}: {e}")
    

    def include_router(self, router: Router) -> None:
        self.routers.append(router)

    async def process_event(self, event) -> None:

        if event.type == "wall_post_new":
            wall = dict_to_obj(event)
            for router in self.routers:
                for handler_data in router.handlers:
                    if all(f())

        elif event.type == VkBotEventType.MESSAGE_NEW:
            
            msg = event.message
            vk_message = VkMessage(self.vk, msg, self.fsm, self.db)

            for router in self.routers:
                for handler_data in router.handlers:
                    #try:
                    if all(f(vk_message) for f in handler_data["filters"]):
                        sig = inspect.signature(handler_data["handler"])
                        params = sig.parameters
                        if len(params) == 2:
                            await handler_data["handler"](event, vk_message)
                        elif len(params) == 3:
                            await handler_data["handler"](event, vk_message, self.db)
                        else:
                            print(f"Ошибка в параметрах функции {handler_data["handler"]}")
                        return
                    #except Exception as e:
                        #logger.error(f"Error in handler: {e}")
            try:
                logger.warning(f"Нет хендлера для: TEXT: {vk_message.text} CMD: {vk_message.payload}")
            except:
                logger.warning(f"Нет хендлера для: TEXT: {vk_message.text}")

    async def start_polling(self) -> None:
        logger.info("Bot started polling...")
        while True:
            #try:
            for event in self.longpoll.listen():

                await self.process_event(event)
            #except Exception as e:
                #logger.error(f"Error in polling: {e}")