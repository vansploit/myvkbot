from typing import Dict, Any, Optional, Callable

class FSM:
	def __init__(self):
		self.storage: Dict[int, Dict[str, Any]] = {}

	def get_state(self, user_id: int) -> Optional[str]:
		"""Получить текущее состояние пользователя"""
		user_data = self.storage.get(user_id)
		return user_data.get('state') if user_data else None

	def get_data(self, user_id: int) -> Dict[str, Any]:
		"""Получить данные состояния пользователя"""
		return self.storage.get(user_id, {}).get("data", {})

	def set_state(self, user_id: int, state: Optional[str]) -> None:
		"""Установить состояние пользователя"""
		if user_id not in self.storage:
			self.storage[user_id] = {'state': None, 'data': {}}
		self.storage[user_id]['state'] = state

	def update_data(self, user_id: int, **kwargs) -> None:
		"""Обновить данные состояния"""
		if user_id not in self.storage:
			self.storage[user_id] = {'state': None, 'data': {}}
		self.storage[user_id]['data'].update(kwargs)

	def reset_state(self, user_id: int, with_data: bool = True) -> None:
		"""Сбросить состояние (и данные, если нужно)"""
		if user_id in self.storage:
			if with_data:
				del self.storage[user_id]
			else:
				self.storage[user_id]['state'] = None


def statefilter(state: str):
	"""Декоратор для фильтрации по состоянию"""
	def decorator(func: Callable):
		def wrapper(event, fsm: FSM, *args, **kwargs):
			user_id = event.object.message['from_id']
			if fsm.get_state(user_id) == state:
				return func(event, fsm, *args, **kwargs)
		return wrapper
	return decorator