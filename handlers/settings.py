from addons.router import Router
from addons.filters import StartsWith
from addons.keyboard import MyKeyboard, start_kb

router = Router()

msgs = {
		"hide": "скрывать",
		"delete": "удалять",
		"leave": "оставлять"
		}
notifs = {
		"all": "все",
		"news": "новости",
		"important": "важное"
		}

def get_settings_kb(msg_s, notif):
	kb = MyKeyboard(inline=True)
	kb.add_buttons(
		("оставлять", "msg_leave", "green" if msg_s == "leave" else "white"),
		("скрывать", "msg_hide", "green" if msg_s == "hide" else "white"),
		("удалять", "msg_delete", "green" if msg_s == "delete" else "white"))
	kb.add_line()
	kb.add_buttons(
		("все", "notif_all", "green" if notif == "all" else "white"),
		("новости", "notif_news", "green" if notif == "news" else "white"),
		("важное", "notif_important", "green" if notif == "important" else "white"))
	kb.add_line()
	kb.add_buttons(("Назад", "back", "red"))
	return kb

#settings_init
@router.command("settings")
async def settings_handler(event, message, db):

	data = db.get_settings(message.from_id)

	kb = get_settings_kb(data["messages"], data["notifications"])

	message.set_state("settings")

	res = await message.answer("⚙Настройки⚙" +\
		f"Сообщения от бота - {msgs[data["messages"]]}" +\
		f"Уведомления - {notifs[data["notifications"]]}", keyboard=kb())
	message.update_data(_id = res[0]["message_id"], msg = data["messages"], notif = data["notifications"])

@router.message(StartsWith("msg_"), state="settings")
async def settings_btn_handler(event, message, db):
	notif = message.data["notif"]

	command = message.payload['command']
	command = command.replace("msg_","")

	kb = get_settings_kb(command, notif)

	db.update_settings(message.from_id, messages=command)

	await message.edit("⚙Настройки⚙" +\
		f"Сообщения от бота - {msgs[command]}" +\
		f"Уведомления - {notifs[notif]}", kb(), message.peer_id, message.data["_id"])
	message.update_data(msg = command, notif = notif)

@router.message(StartsWith("notif_"), state="settings")
async def settings_btn_handler(event, message, db):
	msg = message.data["msg"]

	command = message.payload['command']
	command = command.replace("notif_","")

	kb = get_settings_kb(msg, command)

	db.update_settings(message.from_id, notifications=command)

	await message.edit("⚙Настройки⚙\n" +\
		f"Сообщения от бота - {msgs[msg]}\n" +\
		f"Уведомления - {notifs[command]}\n", kb(), message.peer_id, message.data["_id"])
	message.update_data(msg = msg, notif = command)

@router.command("back", state="settings")
async def back_settings(event, message):
	message.reset_state()
	await message.answer("Добро пожаловать!", keyboard=start_kb())