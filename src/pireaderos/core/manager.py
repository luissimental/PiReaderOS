import logging
import time

from pireaderos.apps import registry
from pireaderos.core import current, event

logger = logging.getLogger(__name__)


class AppManager:
    """Manages the core functionality of PiReaderOS."""

    def __init__(self) -> None:
        """Initialize AppManager."""
        logger.info("Initializing 'AppManager'...")
        self.current = current.CurrentApp()
        self.events = event.EventManager()
        self.events.subscribe("switch_app", self._switch_app)
        self._switch_app("HomeApp")
        logger.info("Initialized 'AppManager'")

    def _switch_app(self, app_name: str) -> None:
        """Clean up and remove current app to load specified app."""
        # Do nothing if app is already loaded
        if self.current.app_name == app_name:
            logger.warning(
                "Switching app to '%s' canceled. App already loaded", app_name
            )
            return

        # Import and get class
        logger.info("Switching app to '%s'...", app_name)
        app_class = registry.get_app_class(app_name)
        if app_class is None:
            logger.error(
                "Switching app to '%s' failed. Cannot retrieve app", app_name
            )
            return

        # Clean up and unload current app
        if self.current.app and self.current.app_name:
            logger.info("Unloading current app '%s'...", self.current.app_name)
            self.current.app.clean_up()
            registry.unload_app_module(self.current.app_name)
            logger.info("Unloaded current app '%s'", self.current.app_name)

        # Instantiate new app
        app_instance = app_class(self.events)
        self.current.app_set(app_instance, app_name)
        logger.info("Switched app to '%s'", app_name)

    def run(self) -> None:
        """Run PiReaderOS."""
        if self.current.app is None and self.current.app_name is None:
            logger.critical(
                "Running 'AppManager' run loop failed. Must have an app loaded"
            )
            msg = "AppManager must have an app loaded to run"
            raise AssertionError(msg)

        logger.info("Running 'AppManager' run loop...")
        try:
            while True:
                time.sleep(0.02)
        except KeyboardInterrupt:
            logger.info(
                "Terminated 'AppManager' run loop. Detected keyboard interrupt"
            )
