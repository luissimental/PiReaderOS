from pireaderos.core import event


class BaseApp:
    """The base class for all apps."""

    def __init__(self, events: event.EventManager) -> None:
        self.events = events

    def clean_up(self) -> None:
        """Clean up when switching out of the app."""
