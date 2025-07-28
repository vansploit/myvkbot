from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def start():
    keyboard = VkKeyboard()  # inline=True — кнопки в самом сообщении
    
    # Кнопка 1 (Оставить заявку)
    keyboard.add_button("У меня есть кое-что", color=VkKeyboardColor.POSITIVE, payload={"command": "new_item"})
            
    # Кнопка 2 (Информация)
    keyboard.add_button("Хочу к вам", color=VkKeyboardColor.PRIMARY, payload={"command": "create_request"})
  
    # Кнопка 3 (Информация)
    keyboard.add_button("Информация", color=VkKeyboardColor.SECONDARY, payload={"command": "info"})
        
    keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE, "command": "exit")
        
    return keyboard.get_keyboard()
    
    
def user_request():
    keyboard = VkKeyboard()
    
    keyboard.add_button("Модератор", color=VkKeyboardColor.PRIMARY, payload={"command": "moderator_ticket"})
        
    keyboard.add_button("Тестер", color=VkKeyboardColor.PRIMARY, payload={"command": "tester_ticket"})
        
    keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE, "command": "exit")
        
    return keyboard.get_keyboard()
        