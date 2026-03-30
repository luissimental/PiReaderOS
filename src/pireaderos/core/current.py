from pireaderos.apps.base import BaseApp


class CurrentApp:
    def __init__(self):
        self._app: BaseApp | None = None
        self._app_name: str | None = None

    @property
    def app(self):
        return self._app

    @property
    def app_name(self):
        return self._app_name

    def app_set(self, app, app_name):
        self._app = app
        self._app_name = app_name
