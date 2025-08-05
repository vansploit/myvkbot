import re
import json
from typing import Optional, Union, List
from .message import VkMessage

from config import ADMIN

class Filter:
    def __call__(self, message: VkMessage) -> bool:
        raise NotImplementedError

class Text(Filter):
    def __init__(self, text: str, ignore_case: bool = True):
        self.text = text.lower() if ignore_case else text
        self.ignore_case = ignore_case

    def __call__(self, message: VkMessage) -> bool:
        msg_text = message.text.lower() if self.ignore_case else message.text
        return msg_text == self.text

class TextContains(Filter):
    def __init__(self, text: str, ignore_case: bool = True):
        self.text = text.lower() if ignore_case else text
        self.ignore_case = ignore_case

    def __call__(self, message: VkMessage) -> bool:
        msg_text = message.text.lower() if self.ignore_case else message.text
        return self.text in msg_text

class Regexp(Filter):
    def __init__(self, pattern: str, flags: int = re.IGNORECASE):
        self.pattern = re.compile(pattern, flags)

    def __call__(self, message: VkMessage) -> bool:
        return bool(self.pattern.search(message.text))

class Command(Filter):
    def __init__(self, command: str):
        self.command = command.lower()

    def __call__(self, message: VkMessage) -> bool:
        try:
            command = message.payload['command']
        except AttributeError:
            command = message.text.lower().replace("/","")
        return command == f'{self.command.replace("/","")}'

class State(Filter):
    def __init__(self, state: str):
        self.state = state

    def __call__(self, message: VkMessage) -> bool:
        
        if self.state == "*":
            return True
        if message.state == None and self.state == ".":
            return True

        return message.state == self.state

class And(Filter):
    def __init__(self, *filters: Filter):
        self.filters = filters

    def __call__(self, message: VkMessage) -> bool:
        return all(f(message) for f in self.filters)

class Or(Filter):
    def __init__(self, *filters: Filter):
        self.filters = filters

    def __call__(self, event: Union['VkMessage', 'wall_post_new']) -> bool:
        if isinstance(event, VkMessage):
            return self.check_message(event)
        elif isinstance(event, wall_post_new):
            return self.check_wall_post(event)
        else:
            raise TypeError(f"Unsupported event type: {type(event)}")

    def check_message(self, message: 'VkMessage') -> bool:
        """Проверяет фильтры для VkMessage."""
        return any(f(message) for f in self.filters)

    def check_wall_post(self, post: 'wall_post_new') -> bool:
        """Проверяет фильтры для wall_post_new."""
        return any(f(post) for f in self.filters)

class IsAdmin(Filter):
    def __call__(self, message: VkMessage) -> bool:
        return message.from_id == ADMIN

class StartsWith(Filter):
    def __init__(self, text: str):
        self.text = text.lower()

    def __call__(self, message: VkMessage):
        try:
            payload = message.payload
            return payload['command'].lower().startswith(self.text)
        except:
            text = message.text
            return text.lower().startswith(self.text)