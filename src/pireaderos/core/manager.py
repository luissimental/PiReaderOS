from pireaderos.apps.registry import get_app_class, unload_app_module
from pireaderos.core.current import CurrentApp
from pireaderos.core.event import EventManager


class AppManager:
    def __init__(self):
        self.current = CurrentApp()
        self.events = EventManager()
        self.events.subscribe("switch_app", self._switch_app)
        self._switch_app("HomeApp")

    def _switch_app(self, app_name: str):
        """Clean up and remove current app to load specified app"""
        if self.current.app_name == app_name:
            return

        app_class = get_app_class(app_name)
        if app_class is None:
            return

        if self.current.app and self.current.app_name:
            self.current.app.clean_up()
            unload_app_module(self.current.app_name)

        app_instance = app_class(self.events)
        self.current.app_set(app_instance, app_name)
