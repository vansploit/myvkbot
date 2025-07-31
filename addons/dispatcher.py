import os
import importlib
import logging
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from typing import List
from .router import Router
from .fsm import FSM
from .message import VkMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VkBotDispatcher:
    def __init__(self, group_id: int, token: str):
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id=group_id)
        self.routers: List[Router] = []
        self.fsm = FSM()

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
        if event.type != VkBotEventType.MESSAGE_NEW:
            return

        msg = event.message
        vk_message = VkMessage(self.vk, msg, self.fsm)

        for router in self.routers:
            for handler_data in router.handlers:
                #try:
                if all(f(vk_message) for f in handler_data["filters"]):
                    await handler_data["handler"](event, vk_message)
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