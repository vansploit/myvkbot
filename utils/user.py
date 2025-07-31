import requests
from config import TOKEN

class User:
	def __init__(self, _id: int, _first_name: str, _last_name: str):
		self._id = _id
		self.first_name = _first_name
		self.last_name = _last_name


def get_users_by_id(*args):
	"""
	Получение информации о *пользовтелях с помощью vk api

	Args:
		*args: id пользователей через запятую

	Returns:
		User: включает id, first_name, last_name
	"""
	result = []

	# Параметры запроса
	params = {
	    'user_ids': ",".join(args),  # ID пользователя (можно несколько через запятую)
	    'fields': 'first_name,last_name',  # Дополнительные поля
	    'access_token': TOKEN,  # Ключ доступа
	    'v': '5.199'  # Версия API
	}

	# Отправка запроса
	response = requests.get('https://api.vk.com/method/users.get', params=params)

	# Обработка ответа
	if response.status_code == 200:
	    data = response.json()
	    if 'response' in data:
	        users = data['response']
	        for user in users:
	            result.append(User(user['id'], user['first_name'], user['last_name']))
	        return result
	    else:
	        print("Error:", data.get('error', 'Unknown error'))
	        return None
	else:
	    print("Request failed with status code:", response.status_code)
	    return None