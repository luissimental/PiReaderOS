from pireaderos.core.current import CurrentApp


class AppManager:
    def __init__(self):
        self.current = CurrentApp()
        self._switch_app("HomeApp")

    def _switch_app(self, app_name: str):
        pass
