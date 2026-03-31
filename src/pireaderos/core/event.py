from typing import Callable


class EventManager:
    def __init__(self):
        self.event_to_subs: dict[str, set[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        """Register a function to be called when an event occurs"""
        if type(event_name) is not str:
            return
        if not callable(callback):
            return

        subscribers = self.event_to_subs.get(event_name)
        if subscribers is None:
            self.event_to_subs[event_name] = subscribers = set()
        subscribers.add(callback)

    def unsubscribe(
        self, event_name: str, callback: Callable,
        _use_dict: dict | None = None
    ):
        """Remove callback function from specified event"""
        if type(event_name) is not str:
            return
        if not callable(callback):
            return

        if _use_dict is None:
            event_to_subs_dict = self.event_to_subs
        else:
            event_to_subs_dict = _use_dict

        subscribers = event_to_subs_dict.get(event_name)
        if subscribers is None:
            return

        subscribers.discard(callback)
        if len(subscribers) == 0:
            del event_to_subs_dict[event_name]

    def unsubscribe_all(self, callback: Callable):
        """Remove callback function from all subscribed events"""
        if not callable(callback):
            return

        event_to_subs_copy = self.event_to_subs.copy()
        for event in self.event_to_subs:
            self.unsubscribe(event, callback, event_to_subs_copy)
        self.event_to_subs = event_to_subs_copy

    def emit(self, event_name: str, *args, **kwargs):
        """Emit event to subscribers with specified args and kwargs"""
        if type(event_name) is not str:
            return

        subscribers = self.event_to_subs.get(event_name)
        if subscribers is None:
            return

        for callback in subscribers:
            try:
                callback(*args, **kwargs)
            except TypeError:
                pass
