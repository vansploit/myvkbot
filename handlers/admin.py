import re
import json
from addons.router import Router
from addons.filters import IsAdmin, CommandArgs
from addons.message import VkMessage
from utils.user import get_user_by_id

from db import UserDatabase

db = UserDatabase()

router = Router()

router.register_global_filter(IsAdmin())

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

@router.command("admin")
async def is_admin_handler(event, message):
	print("Вы админ!")
	await message.answer("Вы админ!")

import sys
@router.command("0", state="*")
async def close_app(event, message):
	sys.exit(0)


@router.message(CommandArgs("ban"))
async def ban_user_handler(event, message):
    args = message.text.split()[1:]  # Удаляем команду сразу при разделении
    user_id = None
    ban_params = {}

    # Функция для обработки аргументов бана
    def process_ban_args(args_list):
        nonlocal ban_params
        if len(args_list) == 1:
            if args_list[0].isdigit():
                ban_params['ban_duration'] = args_list[0]
            else:
                ban_params['reason'] = args_list[0]
        elif len(args_list) == 2:
            # Определяем что есть что (duration всегда число)
            if args_list[0].isdigit():
                ban_params.update({
                    'ban_duration': args_list[0],
                    'reason': args_list[1]
                })
            elif args_list[1].isdigit():
                ban_params.update({
                    'reason': args_list[0],
                    'ban_duration': args_list[1]
                })
            else:
                # Если оба не числа, считаем оба reason (или можно обработать как ошибку)
                ban_params['reason'] = ' '.join(args_list)

    # Пытаемся получить user_id из разных источников
    try:
        if message.reply_message:
            reply_message = message.reply_message
            print(reply_message)
            user_id = reply_message['from_id']
            process_ban_args(args)
    except (AttributeError, json.JSONDecodeError, KeyError):
        pass

    if not user_id and len(message.attachments) > 0:
        try:
            attachments = message.attachments
            if attachments[0].get('type') == "wall_reply":
                user_id = attachments[0]['wall_reply']['from_id']
                process_ban_args(args)
        except (json.JSONDecodeError, KeyError):
            pass

    if not user_id and args:
        if is_vk_url(args[0]):
            user_id = get_user_id_from_url(args[0])
            process_ban_args(args[1:])
        elif args[0].isdigit():
            user_id = args[0]
            process_ban_args(args[1:])

    # Если user_id найден, применяем бан
    if user_id:
        try:
            if db.user_exists(user_id):
                user_data = get_users_by_id(user_id)
                if user_data is not None:
                    db.add_user(
                            user_id,
                            first_name=user_data[0].first_name,
                            last_name=user_data[0].last_name,
                            )
                else:
                    await message.answer(f"Ошибка при добавлении в базу пользователя {user_id}")
                    return
            db.ban_user(user_id, **ban_params)
            print(f"BAN: {user_id} {ban_params}")
        except Exception as e:
            await message.answer(f"Ошибка при бане пользователя: {str(e)}")
    else:
        await message.answer("Не удалось определить пользователя или неверные аргументы!")