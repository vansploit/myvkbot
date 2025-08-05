from typing import Optional, Callable, Dict, List, Any
from .filters import Filter
from .message import VkMessage

class Router:
    def __init__(self):
        self.handlers: List[Dict[str, Any]] = []
        self.global_filters: List[Filter] = []  # Глобальные фильтры для всех обработчиков

    def register_global_filter(self, *filters: Filter) -> None:
        """Добавляет глобальные фильтры для всех обработчиков роутера"""
        self.global_filters.extend(filters)

    def _register_handler(self, filters: List[Filter], handler: Callable) -> None:
        """Регистрирует обработчик с учётом глобальных фильтров"""
        combined_filters = self.global_filters + filters
        self.handlers.append({
            "filters": combined_filters,
            "handler": handler
        })

    def command(self, *commands: str, state: Optional[str] = None, **filters) -> Callable:
        def decorator(handler: Callable) -> Callable:
            filter_list = []
            if commands:
                from .filters import Or, Command
                filter_list.append(Or(*[Command(cmd) for cmd in commands]))
            from .filters import State
            if state:
                filter_list.append(State(state))
            else:
                filter_list.append(State("."))
            for key, value in filters.items():
                if hasattr(self, key):
                    filter_list.append(getattr(self, key)(value))
            self._register_handler(filter_list, handler)
            return handler
        return decorator

    def message(self, *filters: Filter, state: Optional[str] = None) -> Callable:
        def decorator(handler: Callable) -> Callable:
            filter_list = list(filters)
            from .filters import State
            if state:
                filter_list.append(State(state))
            else:
                filter_list.append(State("."))
            self._register_handler(filter_list, handler)
            return handler
        return decorator

    def wall(self, *filters: Filter, state: Optional[str] = None) -> Callable:
        def decorator(handler: Callable) -> Callable:
            filter_list = list(filters)
            from .filters import State
            if state:
                filter_list.append(State(state))
            else:
                filter_list.append(State("."))
            self._register_handler(filter_list, handler)
            return handler
        return decorator