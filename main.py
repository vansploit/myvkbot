import asyncio

from config import TOKEN, GROUP_ID
from addons.dispatcher import VkBotDispatcher

def main():
    dispatcher = VkBotDispatcher(group_id=GROUP_ID, token=TOKEN)
    dispatcher.include_routers_from_folder("handlers")

    asyncio.run(dispatcher.start_polling())

if __name__ == '__main__':
    main()