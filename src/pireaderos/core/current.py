from pireaderos.apps import base


class CurrentApp:
    """Stores the app instance and its name."""

    def __init__(self) -> None:
        self._app: base.BaseApp | None = None
        self._app_name: str | None = None

    @property
    def app(self) -> base.BaseApp | None:
        """The current app instance."""
        return self._app

    @property
    def app_name(self) -> str | None:
        """The current app's name."""
        return self._app_name

    def app_set(self, app: base.BaseApp, app_name: str) -> None:
        """Set the app and app name."""
        self._app = app
        self._app_name = app_name
