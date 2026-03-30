from pireaderos.apps.registry import get_app_class, unload_app_module
from pireaderos.core.current import CurrentApp


class AppManager:
    def __init__(self):
        self.current = CurrentApp()
        self._switch_app("HomeApp")

    def _switch_app(self, app_name: str):
        if self.current.app_name == app_name:
            return

        app_class = get_app_class(app_name)
        if app_class is None:
            return

        if self.current.app and self.current.app_name:
            self.current.app.clean_up()
            unload_app_module(self.current.app_name)

        self.current.app_set(app_class(), app_name)
