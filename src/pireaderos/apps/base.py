from pireaderos.core.event import EventManager


class BaseApp:
    def __init__(self, events: EventManager):
        self.events = events

    def clean_up(self):
        """Called when switching app out for clean up"""
