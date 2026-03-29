class CurrentApp:
    def __init__(self):
        self._app = None
        self._app_name = None

    @property
    def app(self):
        return self._app

    @property
    def app_name(self):
        return self._app_name

    def app_set(self, app, app_name):
        self._app = app
        self._app_name = app_name
