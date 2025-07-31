from typing import Dict, Any, Optional

class FSM:
    def __init__(self):
        self.storage: Dict[int, Dict[str, Any]] = {}

    def get_state(self, user_id: int) -> Optional[str]:
        user_data = self.storage.get(user_id)
        return user_data.get('state') if user_data else None

    def get_data(self, user_id: int) -> Dict[str, Any]:
        return self.storage.get(user_id, {}).get("data", {})

    def set_state(self, user_id: int, state: Optional[str]) -> None:
        if user_id not in self.storage:
            self.storage[user_id] = {'state': None, 'data': {}}
        self.storage[user_id]['state'] = state

    def update_data(self, user_id: int, **kwargs) -> None:
        if user_id not in self.storage:
            self.storage[user_id] = {'state': None, 'data': {}}
        self.storage[user_id]['data'].update(kwargs)

    def reset_state(self, user_id: int, with_data: bool = True) -> None:
        if user_id in self.storage:
            if with_data:
                del self.storage[user_id]
            else:
                self.storage[user_id]['state'] = None