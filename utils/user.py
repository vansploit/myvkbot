import re
import json
import requests
from config import TOKEN

class User:
	def __init__(self, _id: int, _first_name: str, _last_name: str, _domain):
		self._id = _id
		self.first_name = _first_name
		self.last_name = _last_name
		self.domain = _domain


def get_user_by_id(_id):
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
	    'user_ids': str(_id),  # ID пользователя (можно несколько через запятую)
	    'fields': 'first_name,last_name, domain',  # Дополнительные поля
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
	        user = User(users[0]['id'], users[0]['first_name'], users[0]['last_name'], users[0]['domain'])
	        return result
	    else:
	        print("Error:", data.get('error', 'Unknown error'))
	        return None
	else:
	    print("Request failed with status code:", response.status_code)
	    return None

def is_vk_url(url):
    """Проверяет, является ли строка URL профиля VK."""
    vk_patterns = [
        r'^(https?://)?(www\.)?vk\.com/(id\d+|[\w\.-]+)/?$',  # vk.com/id1 или vk.com/durov
        r'^(https?://)?(m\.)?vk\.com/(id\d+|[\w\.-]+)/?$',    # m.vk.com/...
        r'^https?://(vk\.me|vkontakte\.ru)/(id\d+|[\w\.-]+)/?$' # vk.me/... или vkontakte.ru/...
    ]
    
    url = url.strip()
    for pattern in vk_patterns:
        if re.fullmatch(pattern, url, re.IGNORECASE):
            return True
    return False

def get_user_id_from_url(url):
    # Удаляем возможные пробелы и лишние части URL
    url = url.strip().split('/')[-1]
    
    # Если ссылка содержит "id" (например, id12345)
    if url.startswith("id"):
        try:
            return int(url[2:])
        except ValueError:
            return None
    
    # Если ссылка содержит только цифры (например, 12345)
    elif url.isdigit():
        return int(url)
    
    # Если это короткое имя (например, durov)
    else:
        user = get_user_by_id(url)
        if user != None:
            return user._id
        else:
            return None