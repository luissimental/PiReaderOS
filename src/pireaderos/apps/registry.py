import importlib
import sys

from pireaderos.apps.base import BaseApp

APP_REGISTRY: dict[str, str] = {
    "HomeApp": "pireaderos.apps.home",
    "SettingsApp": "pireaderos.apps.settings",
}


def get_app_class(
        app_class: str, _app_registry: dict[str, str] = APP_REGISTRY
) -> type[BaseApp] | None:
    """Dynamically import and return app class"""
    if type(app_class) is not str:
        return

    module_name = _app_registry.get(app_class)
    if module_name is None:
        return
    try:
        module = importlib.import_module(module_name)
        return getattr(module, app_class)
    except ModuleNotFoundError:
        return
    except AttributeError:
        return


def unload_app_module(
    app_class: str, _app_registry: dict[str, str] = APP_REGISTRY
):
    "Remove app module from memory"
    if type(app_class) is not str:
        return False

    module_name = _app_registry.get(app_class)
    if module_name is None:
        return False
    elif module_name in sys.modules:
        del sys.modules[module_name]
        return True
    return False
