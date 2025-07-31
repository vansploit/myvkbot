from typing import Optional, Any, Dict
from .fsm import FSM
from vk_api.utils import get_random_id

class VkMessage:
    def __init__(self, vk_api: Any, original_message: Dict, fsm: FSM):
        self._vk = vk_api
        self._message = original_message
        self._fsm = fsm

        for name, value in self._message.items():
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

    async def answer(self, text: str, **kwargs) -> None:
        self._vk.messages.send(
            peer_id=self.peer_id,
            message=text,
            random_id=get_random_id(),
            **kwargs
        )

    def set_state(self, state: Optional[str]) -> None:
        self._fsm.set_state(self.user_id, state)

    def update_data(self, **kwargs) -> None:
        self._fsm.update_data(self.user_id, **kwargs)

    def reset_state(self, with_data: bool = True) -> None:
        self._fsm.reset_state(self.user_id, with_data)