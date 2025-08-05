import json
from addons.router import Router
from addons.filters import IsAdmin
from addons.message import VkMessage
from addons.keyboard import MyKeyboard, confirm_kb, back_btn
from utils.user import get_user_by_id, is_vk_url, get_user_id_from_url

router = Router()

router.register_global_filter(IsAdmin())



@router.command("admin")
async def is_admin_handler(event, message):
	print("Вы админ!")
	await message.answer("Вы админ!")

import sys
@router.command("0", state="*")
async def close_app(event, message):
	sys.exit(0)


@router.command("ban")
async def ban_handler(event, message, db):
    user_id = None
    text = message.text.split()
    if len(text) > 1 and is_vk_url(text[1]):
        user_id = get_user_id_from_url(text[1])
    if hasattr(message, "attachments") and len(message.attachments) > 0:
        attachments = message.attachments
        if attachments[0].get('type') == "wall_reply":
            user_id = attachments[0]['wall_reply']['from_id']
    elif hasattr(message, "reply_message"):
        reply_message = message.reply_message
        user_id = reply_message['from_id']

    if user_id != None:
        if db.user_exists(user_id):
            if db.is_banned(user_id):
                await message.answer("Пользователь найден в базе!\nОн уже забанен!")
                return
        else:
            user_data = get_user_by_id(user_id)
            db.add_user(user_id, first_name=user_data.first_name, last_name=user_data.last_name)
        message.set_state("ban_time")
        message.update_data(ban_id=user_id)
        continue_kb = MyKeyboard(inline=True)
        continue_kb.add_buttons(("Навсегда", "continue", "red"))
        await message.answer("Время:", keyboard=continue_kb())
    else:
        message.set_state("ban_id")
        await message.answer("Введите id пользователя или ссылку на его страницу:")


@router.message(state="ban_id")
async def ban_id_h(event, message):
    if message.text.isdigit():
        user_id = message.text
    elif is_vk_url(message.text):
        user_id = get_user_id_from_url(message.text)
    if user_id != None:
        message.set_state("ban_time")
        message.update_data(ban_id=user_id)
        continue_kb = MyKeyboard(inline=True)
        continue_kb.add_buttons(("Навсегда", "continue", "red"))
        await message.answer("Время:", keyboard=continue_kb())
    else:
        await message.answer("Ошибка! Не получилось получить id!", keyboard=back_btn())


@router.command("continue", state="ban_time")
async def ban_time_c(event, message):
    message.set_state("ban_reason")
    message.update_data(ban_time=None)
    continue_kb = MyKeyboard(inline=True)
    continue_kb.add_buttons(("Без причины", "continue", "red"))
    await message.answer("Введите причину бана:", keyboard=continue_kb())



@router.message(state="ban_time")
async def ban_time_h(event, message):
    if message.text.isdigit():
        if int(message.text) == 0:
            message.update_data(ban_time=None)
        else:
            message.update_data(ban_time=message.text)
        message.set_state("ban_reason")
        continue_kb = MyKeyboard(inline=True)
        continue_kb.add_buttons(("Без причины", "continue", "red"))
        await message.answer("Введите причину бана:", keyboard=continue_kb())
    else:
        await message.answer("Введите время бана в минутах!")


@router.command("continue", state="ban_reason")
async def ban_reason_c(event, message):
    message.set_state("confirm_ban")
    message.update_data(ban_reason=None)
    data = message.data
    await message.answer(f"Подтвердите бан пользователя:\n" +\
        f"ID: {data["ban_id"]}\n" +\
        f"Время: {data["ban_time"] if data["ban_time"] != None else "Навсегда"}\n" +\
        f"Причина: {data["ban_reason"] if data["ban_reason"] != None else ""}", keyboard=confirm_kb())

@router.message(state="ban_reason")
async def ban_reason_h(event, message):
    ban_reason = message.text.lower()
    data = message.data
    message.update_data(ban_reason=ban_reason)
    message.set_state("confirm_ban")
    await message.answer(f"Подтвердите бан пользователя:\n" +\
        f"ID: {data["ban_id"]}\n" +\
        f"Время: {data["ban_time"] if data["ban_time"] != None else "Навсегда"}\n" +\
        f"Причина: {data["ban_reason"] if data["ban_reason"] != None else ""}", keyboard=confirm_kb())

@router.command("cancel", state="confirm_ban")
async def cancel_ban(event, message):
    message.reset_state()
    await message.answer("Бан отменяется")

@router.command("confirm", state="confirm_ban")
async def ban_confirm(event, message, db):
    data = message.data
    user = get_user_by_id(data["ban_id"])
    res = db.ban_user(data["ban_id"], data["ban_reason"], data["ban_time"])
    if res:
        message.reset_state()
        await message.answer("#BAN\n" +\
            f"Пользователь забанен\n" + \
            f"ID: {data["ban_id"]}\n" +\
            f"Имя: {user.first_name}\n" +\
            f"URL: vk.com/{user.domain}\n" +\
            "=============================================\n" +\
            f"Время бана: {data["ban_time"]}\n" +\
            f"Причина: {data["ban_reason"]}\n")
    else:
        message.reset_state()
        await message.answer("Ошибка!")

@router.command("unban")
async def unban_handler(event, message, db):
    args_msg = message.text.split()
    if len(args_msg) > 1:
        if is_vk_url(args_msg[1]):
            unban_id = get_user_id_from_url(args_msg[1])
        elif args_msg[1].isdigit():
            unban_id = args_msg[1]
        else:
            await message.answer("Ошибка! Неверный id!")
        user = db.get_user(unban_id)
        ban_info = db.is_banned(unban_id)
        message.update_data(user=user)
        message.set_state("confirm_unban", keyboard=confirm_kb())
        await message.answer("Разбанить пользователя?\n"+\
            f"ID: {user["user_id"]}\n"+\
            f"Имя: {user["first_name"]}\n"+\
            f"URL: {user["url"]}\n"+\
            "==============================================\n"+\
            f"Время бана: {ban_info["ban_time"]}\n"+\
            f"Время разбана: {ban_info["unban_time"]}\n"+\
            f"Причина: {ban_info["reason"]}")
    else:
        message.set_state("unban_id")
        await message.answer("Введите id или url пользователя:")

@router.message(state="unban_id")
async def unban_id_h(event, message, db):
    if is_vk_url(message.text):
        unban_id = get_user_id_from_url(message.text)
    elif message.text.isdigit():
        unban_id = message.text
    else:
        await message.answer("Ошибка! Неверный id!")
    user = db.get_user(unban_id)
    ban_info = db.is_banned(unban_id)
    message.update_data(user=user)
    message.set_state("confirm_unban", keyboard=confirm_kb())
    await message.answer("Разбанить пользователя?\n"+\
        f"ID: {user["user_id"]}\n"+\
        f"Имя: {user["first_name"]}\n"+\
        f"URL: {user["url"]}\n"+\
        "==============================================\n"+\
        f"Время бана: {ban_info["ban_time"]}\n"+\
        f"Время разбана: {ban_info["unban_time"]}\n"+\
        f"Причина: {ban_info["reason"]}")

@router.command("confirm", state="confirm_unban")
async def final_unban(event, message):
    user = message.data["user"]
    res = db.unban_user(user.user_id)
    message.reset_state()
    if res:
        await message.answer(f"Пользователь {user["user_id"]} успешно разбанен!")
    else:
        await message.answer(f"Ошибка при разбане пользователя {user["user_id"]}!")