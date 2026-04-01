import importlib
import logging
import sys

from pireaderos.apps.base import BaseApp


logger = logging.getLogger(__name__)

APP_REGISTRY: dict[str, str] = {
    "HomeApp": "pireaderos.apps.home",
    "SettingsApp": "pireaderos.apps.settings",
}


def get_app_class(
        app_class: str, _app_registry: dict[str, str] = APP_REGISTRY
) -> type[BaseApp] | None:
    """Dynamically import and return app class"""
    # Check that argument type is valid
    if type(app_class) is not str:
        logger.error(
            "Getting app class failed. "
            f"App class '{app_class}' is not a string"
        )
        return

    # Retrieve module name in registry
    module_name = _app_registry.get(app_class)
    if module_name is None:
        logger.error(
            "Getting app class failed. "
            f"App class '{app_class}' not in registry"
        )
        return

    # Import module and return app class
    try:
        module = importlib.import_module(module_name)
        return getattr(module, app_class)
    except ModuleNotFoundError:
        logger.error(
            f"Getting app class '{app_class}' failed. "
            f"Module '{module_name}' not found"
        )
    except AttributeError:
        logger.error(
            f"Getting app class '{app_class}' failed. "
            f"App class not found in module '{module_name}'"
        )


def unload_app_module(
    app_class: str, _app_registry: dict[str, str] = APP_REGISTRY
):
    "Remove app module from memory"
    # Check that argument type is valid
    if type(app_class) is not str:
        logger.error(
            "Unloading app module failed. "
            f"App class '{app_class}' is not a string"
        )
        return False

    # Retrieve module name in registry
    module_name = _app_registry.get(app_class)
    if module_name is None:
        logger.error(
            "Unloading app module failed. "
            f"App class '{app_class}' not in registry"
        )
        return False

    # Remove module from memory
    if module_name in sys.modules:
        del sys.modules[module_name]
        return True

    logger.error(
        f"Unloading app module with app_class '{app_class}' failed. "
        f"Module '{module_name}' is not loaded"
    )
    return False
