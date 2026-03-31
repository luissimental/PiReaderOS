import pytest

from pireaderos.apps.home import HomeApp
from pireaderos.apps.registry import APP_REGISTRY
from pireaderos.apps.settings import SettingsApp
from pireaderos.core.current import CurrentApp
from pireaderos.core.manager import AppManager


@pytest.fixture
def mock_current_app_with(mocker):
    """Factory fixture to mock CurrentApp with custom app and app_name"""
    def _mock_func(app, app_name):
        mock = mocker.patch("pireaderos.core.manager.CurrentApp")
        instance = mock.return_value
        instance.app = app
        instance.app_name = app_name
        return instance
    return _mock_func


@pytest.fixture
def mock_get_app_class(mocker):
    return mocker.patch("pireaderos.core.manager.get_app_class")


@pytest.fixture
def mock_unload_app_module(mocker):
    return mocker.patch("pireaderos.core.manager.unload_app_module")


@pytest.fixture
def app_manager_unittest(mocker):
    """Patch __init__ for isolation"""
    mocker.patch.object(AppManager, "__init__", return_value=None)
    manager = AppManager()
    manager.events = mocker.Mock()
    return manager


@pytest.fixture
def app_manager_integration(mocker):
    """Patch __init__ and app methods for isolation"""
    mocker.patch.object(AppManager, "__init__", return_value=None)
    for class_name, module_name in APP_REGISTRY.items():
        # Patch in original module due to dynamic import
        mocker.patch(f"{module_name}.{class_name}.__init__",
                     return_value=None)
        mocker.patch(f"{module_name}.{class_name}.clean_up",
                     return_value=None)
    manager = AppManager()
    manager.events = mocker.Mock()
    return manager


class TestAppManagerInitialization:
    def test_init_is_working_unittest(self, mocker):
        MockCurrentApp = mocker.patch("pireaderos.core.manager.CurrentApp")
        MockEventMgr = mocker.patch("pireaderos.core.manager.EventManager")
        mock_events_instance = MockEventMgr.return_value
        MockSwitchApp = mocker.patch(
            "pireaderos.core.manager.AppManager._switch_app")

        manager = AppManager()

        MockCurrentApp.assert_called_once()
        assert manager.current is MockCurrentApp.return_value
        MockEventMgr.assert_called_once()
        mock_events_instance.subscribe.assert_called_once_with(
            "switch_app", MockSwitchApp)
        MockSwitchApp.assert_called_once_with("HomeApp")


class TestAppManagerSwitchingApp:
    def test_app_name_is_valid_with_different_existing_app_unittest(
        self, mocker, mock_get_app_class, mock_current_app_with,
        mock_unload_app_module, app_manager_unittest
    ):
        """Switch app successfully when a different app is already loaded"""
        mock_new_app_class = mocker.Mock()
        mock_get_app_class.return_value = mock_new_app_class  # new app class

        mock_current_instance = mock_current_app_with(
            mocker.Mock(), "OldAppName")  # old app

        app_manager_unittest.current = mock_current_instance
        app_manager_unittest._switch_app("NewAppName")

        # get_app_class("NewAppName")
        mock_get_app_class.assert_called_once_with("NewAppName")
        # self.current.app.cleanup()
        mock_current_instance.app.clean_up.assert_called_once()
        # unload_app_module("OldAppName")
        mock_unload_app_module.assert_called_once_with("OldAppName")
        # app_class(self.events)
        mock_new_app_class.assert_called_once_with(app_manager_unittest.events)
        # app_set(app_class(), "NewAppName")
        mock_current_instance.app_set.assert_called_once_with(
            mock_new_app_class.return_value, "NewAppName")

    def test_app_name_is_valid_with_different_existing_app_integration(
        self, app_manager_integration
    ):
        """Switch app successfully when a different app is already loaded"""
        app_manager_integration.current = CurrentApp()
        app_manager_integration.current._app = HomeApp(
            app_manager_integration.events)
        app_manager_integration.current._app_name = "HomeApp"
        app_manager_integration._switch_app("SettingsApp")

        assert isinstance(app_manager_integration.current.app, SettingsApp)
        assert app_manager_integration.current.app_name == "SettingsApp"

    def test_app_name_is_valid_with_no_existing_app_unittest(
        self, mocker, mock_get_app_class, mock_current_app_with,
        mock_unload_app_module, app_manager_unittest
    ):
        """Switch app successfully when no app is loaded"""
        mock_new_app_class = mocker.Mock()
        mock_get_app_class.return_value = mock_new_app_class  # new app class

        mock_existing_app = mocker.Mock()
        mock_current_instance = mock_current_app_with(None, None)  # old app

        app_manager_unittest.current = mock_current_instance
        app_manager_unittest._switch_app("NewAppName")

        # get_app_class("NewAppName")
        mock_get_app_class.assert_called_once_with("NewAppName")
        # self.current.app.cleanup()
        mock_existing_app.clean_up.assert_not_called()
        # unload_app_module("OldAppName")
        mock_unload_app_module.assert_not_called()
        # app_class(self.events)
        mock_new_app_class.assert_called_once_with(app_manager_unittest.events)
        # app_set(app_class(), "NewAppName")
        mock_current_instance.app_set.assert_called_once_with(
            mock_new_app_class.return_value, "NewAppName")

    @pytest.mark.parametrize("app_name", APP_REGISTRY.keys())
    def test_app_name_is_valid_with_no_existing_app_integration(
        self, app_manager_integration, app_name
    ):
        """Switch app successfully when no app is loaded"""
        app_manager_integration.current = CurrentApp()
        app_manager_integration._switch_app(app_name)

        class_name = app_manager_integration.current.app.__class__.__name__
        assert class_name == app_name
        assert app_manager_integration.current.app_name == app_name

    def test_app_name_is_valid_with_same_existing_app_unittest(
        self, mocker, mock_get_app_class, mock_current_app_with,
        mock_unload_app_module, app_manager_unittest
    ):
        """Switch app successfully when the same app is already loaded"""
        mock_new_app_class = mocker.Mock()
        mock_get_app_class.return_value = mock_new_app_class  # new app class

        mock_existing_app = mocker.Mock()
        mock_existing_app.name = "OldAppName"
        mock_current_instance = mock_current_app_with(
            mock_existing_app, mock_existing_app.name)  # old app

        app_manager_unittest.current = mock_current_instance
        app_manager_unittest._switch_app("OldAppName")

        # get_app_class("OldAppName")
        mock_get_app_class.assert_not_called()
        # self.current.app.cleanup()
        mock_existing_app.clean_up.assert_not_called()
        # unload_app_module("OldAppName")
        mock_unload_app_module.assert_not_called()
        # app_class(self.events)
        mock_new_app_class.assert_not_called()
        # app_set(app_class(), "OldAppName")
        mock_new_app_class.assert_not_called()
        mock_current_instance.app_set.assert_not_called()

        assert app_manager_unittest.current.app is mock_existing_app
        assert app_manager_unittest.current.app_name is mock_existing_app.name

    def test_app_name_is_valid_with_same_existing_app_integration(
        self, app_manager_integration
    ):
        """Switch app successfully when the same app is already loaded"""
        app_manager_integration.current = CurrentApp()
        app_manager_integration.current._app = existing_app = HomeApp(
            app_manager_integration.events)
        app_manager_integration.current._app_name = existing_app_name = "HomeApp"
        app_manager_integration._switch_app("HomeApp")

        assert app_manager_integration.current.app is existing_app
        assert app_manager_integration.current.app_name is existing_app_name

    @pytest.mark.parametrize("app_name", ["", "InvalidApp", None, 1, object()])
    def test_app_name_is_invalid_unittest(
        self, mocker, mock_get_app_class, mock_current_app_with,
        mock_unload_app_module, app_manager_unittest,  app_name
    ):
        """Switch app fails when app_name is not registered or a string"""
        mock_new_app_class = mocker.Mock()
        mock_get_app_class.return_value = None  # new app class

        mock_existing_app = mocker.Mock()
        mock_current_instance = mock_current_app_with(
            mock_existing_app, "HomeApp")  # old app

        app_manager_unittest.current = mock_current_instance
        app_manager_unittest._switch_app(app_name)

        # get_app_class("NewAppName")
        mock_get_app_class.assert_called_once_with(app_name)
        # self.current.app.cleanup()
        mock_existing_app.clean_up.assert_not_called()
        # unload_app_module("OldAppName")
        mock_unload_app_module.assert_not_called()
        # app_class(self.events)
        mock_new_app_class.assert_not_called()
        # app_set(app_class(), "NewAppName")
        mock_current_instance.app_set.assert_not_called()

    @pytest.mark.parametrize("app_name", ["", "InvalidApp", None, 1, object()])
    def test_app_name_is_invalid_integration(
        self, app_manager_integration, app_name
    ):
        """Switch app fails when app_name is not registered or a string"""
        app_manager_integration.current = CurrentApp()
        app_manager_integration.current._app = existing_app = HomeApp(
            app_manager_integration.events)
        app_manager_integration.current._app_name = existing_app_name = "HomeApp"
        app_manager_integration._switch_app(app_name)

        assert app_manager_integration.current.app is existing_app
        assert app_manager_integration.current.app_name is existing_app_name
