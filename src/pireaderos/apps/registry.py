import importlib
import logging
import sys

from pireaderos.apps import base

logger = logging.getLogger(__name__)

APP_REGISTRY: dict[str, str] = {
    "HomeApp": "pireaderos.apps.home",
    "SettingsApp": "pireaderos.apps.settings",
}


def get_app_class(
    app_class: str, _app_registry: dict[str, str] = APP_REGISTRY
) -> type[base.BaseApp] | None:
    """Import and return the app class."""
    # Check that the argument type is valid
    if type(app_class) is not str:
        logger.error(
            "Getting app class failed. App class '%s' is not a string",
            app_class,
        )
        return None

    # Retrieve module name in registry
    module_name = _app_registry.get(app_class)
    if module_name is None:
        logger.error(
            "Getting app class failed. App class '%s' not in registry",
            app_class,
        )
        return None

    # Import module and return app class
    try:
        module = importlib.import_module(module_name)
        return getattr(module, app_class)
    except ModuleNotFoundError:
        logger.exception(
            "Getting app class '%s' failed. Module '%s' not found",
            app_class,
            module_name,
        )
    except AttributeError:
        logger.exception(
            "Getting app class '%s' failed. "
            "App class not found in module '%s'",
            app_class,
            module_name,
        )


def unload_app_module(
    app_class: str, _app_registry: dict[str, str] = APP_REGISTRY
) -> bool:
    """Remove the app_class's module from memory."""
    # Check that argument type is valid
    if type(app_class) is not str:
        logger.error(
            "Unloading app module failed. App class '%s' is not a string",
            app_class,
        )
        return False

    # Retrieve module name in registry
    module_name = _app_registry.get(app_class)
    if module_name is None:
        logger.error(
            "Unloading app module failed. App class '%s' not in registry",
            app_class,
        )
        return False

    # Remove module from memory
    if module_name in sys.modules:
        del sys.modules[module_name]
        return True

    logger.error(
        "Unloading app module with app_class '%s' failed. "
        "Module '%s' is not loaded",
        app_class,
        module_name,
    )
    return False
