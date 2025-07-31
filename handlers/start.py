from vk_api.keyboard import VkKeyboard
from addons.router import Router
from addons.keyboard import MyKeyboard
from addons.filters import StartsWith
import json

router = Router()

@router.command("start")
async def start_handler(event, message):

	start_kb = MyKeyboard(inline=True)
	start_kb.add_buttons(
							("Хочу к вам", "create_request", "blue"),
							("Информация", "info", "white")
                        )

	await message.answer("Добро пожаловать!", keyboard=start_kb())

#create_request main
@router.command("create_request")
async def create_request_handler(event, message):

	request_kb = MyKeyboard(inline=True)
	request_kb.add_buttons(
						    ("Модератор", "ticket_moderator", "blue"),
                            ("Тестер", "ticket_tester", "blue"),
                            ("Назад", "back", "red"))

	message.set_state("create_request")
	await message.answer(
						"Выберите должность:",
						keyboard=request_kb()
						)

#create_request back
@router.command("back", state="create_request")
async def create_request_back(event, message):
	message.reset_state()
	await start_handler(event, message)

#Вопрос 1:
@router.message(StartsWith("ticket_"), state="create_request")
async def tickets_ticket_handler(event, message):
	payload = json.loads(message.payload)
	message.update_data(ticket=payload['command'].replace("ticket_", ""))
	message.set_state("tickets_1")
	await message.answer("Как мне вас звать?(нельзя изменить)")

#Подтверждение вопроса 1
@router.message(state="tickets_1")
async def tickets_name(event, message):

	message.update_data(name=message.text)

	confirm_kb = MyKeyboard(inline=True)
	confirm_kb.add_buttons(
						    ("Да", "confirm_name", "green"),
						    ("Нет", "cancel_name", "red"))

	message.set_state("tickets_2")
	await message.answer(
						f"Мне звать вас {message.text}?",
						keyboard=confirm_kb()
						)

#Подтвердить имя!
#Вопрос 2:
@router.command("confirm_name", state="tickets_2")
async def tickets_description(event, message):
	message.set_state("tickets_3")
	await message.answer("Принято! Теперь расскажите о себе(чем больше тем лучше)")

#Отменить имя!
@router.command("cancel_name", state="tickets_3")
async def cancel_name(event, message):
	message.set_state("tickets_2")
	await message.answer("Ок! Напишите имя еще раз!")

#Подтверждение вопроса 2
@router.message(state="tickets_3")
async def tickets_description_confirm_handler(event, message):

	message.set_state("tickets_4")
	message.update_data(description=message.text)

	confirm_kb = MyKeyboard(inline=True)
	confirm_kb.add_buttons(
		("Да", "confirm_description", "green"),
		("Нет", "cancel_description", "red"))

	await message.answer(
		                "Подтвердите описание...",
						keyboard=confirm_kb()
						)

#Подтвердить вопрос 2
@router.command("confirm_description", state="tickets_4")
async def tickets_description_confirm(event, message):

	message.set_state("tickets_end")

	for key, value in message.data.items():
		print(f"{key}: {value}")

	back_btn = MyKeyboard(inline=True)
	back_btn.add_buttons(("Выйти", "exit", "red"))

	await message.answer(
						"Заявка принята! Если вас примут, то с вами свяжется модератор!",
						keyboard=back_btn())

#Отменить вопрос 2
@router.command("cancel_description", state="tickets_4")
async def tickets_description_cancel(event, message):
	message.set_state("tickets_3")
	await message.answer("Расскажите о себе еще раз:")

#Выход в меню выбора
@router.command("exit", state="tickets_end")
async def exit_tickets_handler(event, message):
	message.reset_state()
	await create_request_handler(event, message)