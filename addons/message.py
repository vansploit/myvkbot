from typing import Optional, Any, Dict
from .fsm import FSM
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
from config import GROUP_ID
import json
from expiringdict import ExpiringDict
import time
from db import UserDatabase

# Создаем словарь с временем жизни записей 5 секунд
messsage_to_hide = ExpiringDict(max_len=100, max_age_seconds=300)

messsage_to_delete = ExpiringDict(max_len=100, max_age_seconds=300)

class VkMessage:
    def __init__(self, vk_api: Any, original_message: Dict, fsm: FSM, db: UserDatabase):
        self._vk = vk_api
        self._message = original_message
        self._fsm = fsm
        self.db = db
        if db.user_exists(self._message.from_id):
            self.hd_message = self.db.get_settings(self._message.from_id)["messages"]
        else:
            self.hd_message = "important"

        for name, value in self._message.items():
            if name == "payload":
                value = json.loads(value)
            setattr(self, name, value)

    @property
    def user_id(self) -> int:
        return self._message["from_id"]

    @property
    def state(self) -> Optional[str]:
        return self._fsm.get_state(self.user_id)

    @property
    def data(self) -> Dict[str, Any]:
        return self._fsm.get_data(self.user_id)

    @property
    def from_user(self) -> bool:
        return self.from_id > 0

    @property
    def from_group(self) -> bool:
        return self.from_id < 0

    async def answer(self, text: str, **kwargs) -> None:
        res = self._vk.messages.send(
                peer_ids=str(self.peer_id),
                message=text,
                random_id=get_random_id(),
                **kwargs
                )
        if self.hd_message == "delete":
            if res[0]["peer_id"] in messsage_to_delete:
                try:
                    await self.delete(res[0]["peer_id"], messsage_to_delete[res[0]["peer_id"]])
                except:
                    print("Ошибка удаления сообщения!")
            messsage_to_delete[res[0]["peer_id"]] = res[0]["message_id"]
        elif self.hd_message == "hide":
            if res[0]["peer_id"] in messsage_to_hide:
                try:
                    await self.edit("✨[это скрытое сообщение]✨", VkKeyboard.get_empty_keyboard(), res[0]["peer_id"], messsage_to_hide[res[0]["peer_id"]])
                except:
                    print("Ошибка изменения сообщения!")
            messsage_to_hide[res[0]["peer_id"]] = res[0]["message_id"]
        return res

    def set_state(self, state: Optional[str]) -> None:
        self._fsm.set_state(self.user_id, state)

    def update_data(self, **kwargs) -> None:
        self._fsm.update_data(self.user_id, **kwargs)

    def reset_state(self, with_data: bool = True) -> None:
        self._fsm.reset_state(self.user_id, with_data)

    async def delete(self, peer_id, _id):
        self._vk.messages.delete(
            peer_id = peer_id,
            message_ids = _id,
            delete_for_all = 1
            )
    async def edit(self, msg, keyboard, peer_id, _id):
        self._vk.messages.edit(
            peer_id = peer_id,
            message_id = _id,
            message = msg,
            keyboard = keyboard
            )