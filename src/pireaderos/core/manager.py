import logging
import time

from pireaderos.apps.registry import get_app_class, unload_app_module
from pireaderos.core.current import CurrentApp
from pireaderos.core.event import EventManager


logger = logging.getLogger(__name__)


class AppManager:
    def __init__(self):
        logger.info("Initializing 'AppManager'...")
        self.current = CurrentApp()
        self.events = EventManager()
        self.events.subscribe("switch_app", self._switch_app)
        self._switch_app("HomeApp")
        logger.info("Initialized 'AppManager'")

    def _switch_app(self, app_name: str):
        """Clean up and remove current app to load specified app"""
        # Do nothing if app is already loaded
        if self.current.app_name == app_name:
            logger.warning(
                f"Switching app to '{app_name}' canceled. App already loaded")
            return

        # Import and get class
        logger.info(f"Switching app to '{app_name}'...")
        app_class = get_app_class(app_name)
        if app_class is None:
            logger.error(
                f"Switching app to '{app_name}' failed. Cannot retrieve app")
            return

        # Clean up and unload current app
        if self.current.app and self.current.app_name:
            logger.info(f"Unloading current app '{self.current.app_name}'...")
            self.current.app.clean_up()
            unload_app_module(self.current.app_name)
            logger.info(f"Unloaded current app '{self.current.app_name}'")

        # Instantiate new app
        app_instance = app_class(self.events)
        self.current.app_set(app_instance, app_name)
        logger.info(f"Switched app to '{app_name}'")

    def run(self):
        if self.current.app is None and self.current.app_name is None:
            logger.critical(
                "Running 'AppManager' run loop failed. "
                "Must have an app loaded"
            )
            raise AssertionError("AppManager must have an app loaded to run")

        logger.info("Running 'AppManager' run loop...")
        try:
            while True:
                time.sleep(0.02)
        except KeyboardInterrupt:
            logger.info(
                "Terminated 'AppManager' run loop. "
                "Detected keyboard interrupt"
            )
