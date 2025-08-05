from vk_api.keyboard import VkKeyboard, VkKeyboardColor

class MyKeyboard:
    def __init__(self, inline=False):
        self.keyboard = VkKeyboard(inline=inline)
        self.colors = {
                    "green":VkKeyboardColor.POSITIVE,
                    "blue": VkKeyboardColor.PRIMARY,
                    "red": VkKeyboardColor.NEGATIVE,
                    'white':VkKeyboardColor.SECONDARY}

    def add_buttons(self, *args):
        for button in args:
            if button == "line":
                self.keyboard.add_line()
            else:
                self.keyboard.add_button(
                                        label = button[0],
                                        color=self.colors[button[2]] if len(button) > 2 else None,
                                        payload={'command': button[1]})

    def add_line(self):
        self.keyboard.add_line()

    def __call__(self):
        return self.keyboard.get_keyboard()

    def as_obj(self):
        return self.keyboard


confirm_kb = MyKeyboard(inline=True)
confirm_kb.add_buttons(
                        ("Да", "confirm", "green"),
                        ("Нет", "cancel", "red"))
back_btn = MyKeyboard(inline=True)
back_btn.add_buttons(("Отмена", "exit", "red"))

start_kb = MyKeyboard(inline=True)
start_kb.add_buttons(
                    ("Отправить", "applications", "green"),
                    "line",
                    ("Заявка в команду", "create_request", "green"),
                    "line",
                    ("Настройки", "settings", "blue"),
                    "line",
                    ("Информация", "info")
                    )