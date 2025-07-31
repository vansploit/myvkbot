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
            self.keyboard.add_button(
                                        label = button[0],
                                        color=self.colors[button[2]] if len(button) > 2 else None,
                                        payload={'command': button[1]})

    def __call__(self):
        return self.keyboard.get_keyboard()

    def as_obj(self):
        return self.keyboard