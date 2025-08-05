from vk_api.keyboard import VkKeyboard
from addons.router import Router
from addons.keyboard import MyKeyboard, start_kb

router = Router()

@router.command("start")
async def start_handler(event, message, db):

	db.add_user(message.from_id)

	await message.answer("Добро пожаловать!", keyboard=start_kb())