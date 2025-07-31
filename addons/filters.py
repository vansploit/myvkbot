import re
import json
from typing import Optional, List
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

    def has_arguments(self, command):
        # Удаляем все пробелы и табы в начале и конце строки
        stripped = command.strip()
        # Проверяем, есть ли после команды что-то кроме пробелов
        # Используем регулярное выражение для разделения команды и аргументов
        match = re.match(r'^\S+\s+\S+', stripped)
        return bool(match)

    def __call__(self, message: VkMessage) -> bool:
        try:
            command = json.loads(message.payload)['command']
        except AttributeError:
            command = message.text.lower().replace("/","")
        if not self.has_arguments(command):
            return command == f'{self.command.replace("/","")}'
        else:
            return False

class CommandArgs(Filter):
    def __init__(self, command: str):
        self.command = command.lower()

    def has_arguments(self, command):
        # Удаляем все пробелы и табы в начале и конце строки
        stripped = command.strip()
        # Проверяем, есть ли после команды что-то кроме пробелов
        # Используем регулярное выражение для разделения команды и аргументов
        match = re.match(r'^\S+\s+\S+', stripped)
        return bool(match)

    def __call__(self, message: VkMessage) -> bool:
        command = message.text.lower()
        if self.has_arguments(command):
            return self.command.replace("/","") == command.replace("/","").split()[0]
        else:
            return False

class State(Filter):
    def __init__(self, state: str):
        self.state = state

    def __call__(self, message: VkMessage) -> bool:
        if self.state == "*":
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

    def __call__(self, message: VkMessage) -> bool:
        return any(f(message) for f in self.filters)

class IsAdmin(Filter):
    def __call__(self, message: VkMessage) -> bool:
        return message.from_id == ADMIN

class StartsWith(Filter):
    def __init__(self, text: str):
        self.text = text.lower()

    def __call__(self, message: VkMessage):
        try:
            payload = json.loads(message.payload)
            return payload['command'].lower().startswith(self.text)
        except:
            text = message.text
            return text.lower().startswith(self.text)