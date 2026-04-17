from collections.abc import Callable

import pytest
import pytest_mock

from pireaderos.apps import home, registry, settings
from pireaderos.core import current
from pireaderos.core import manager as manager_mod


@pytest.fixture
def mock_current_app_with(
    mocker: pytest_mock.MockerFixture,
) -> Callable[..., pytest_mock.MockType]:
    """Create factory fixture to mock CurrentApp with app and app_name."""

    def _mock_func(app: object, app_name: object) -> pytest_mock.MockType:
        mock = mocker.patch("pireaderos.core.manager.current.CurrentApp")
        instance = mock.return_value
        instance.app = app
        instance.app_name = app_name
        return instance

    return _mock_func


@pytest.fixture
def mock_get_app_class(
    mocker: pytest_mock.MockerFixture,
) -> pytest_mock.MockType:
    """Return patched get_app_class."""
    return mocker.patch("pireaderos.core.manager.registry.get_app_class")


@pytest.fixture
def mock_unload_app_module(
    mocker: pytest_mock.MockerFixture,
) -> pytest_mock.MockType:
    """Return patched unload_app_module."""
    return mocker.patch("pireaderos.core.manager.registry.unload_app_module")


@pytest.fixture
def app_manager_unittest(
    mocker: pytest_mock.MockerFixture,
) -> manager_mod.AppManager:
    """Patch __init__ for isolation."""
    mocker.patch.object(manager_mod.AppManager, "__init__", return_value=None)
    manager = manager_mod.AppManager()
    manager.events = mocker.Mock()
    return manager


@pytest.fixture
def app_manager_integration(
    mocker: pytest_mock.MockerFixture,
) -> manager_mod.AppManager:
    """Patch __init__ and app methods for isolation."""
    mocker.patch.object(manager_mod.AppManager, "__init__", return_value=None)
    for class_name, module_name in registry.APP_REGISTRY.items():
        # Patch in original module due to dynamic import
        mocker.patch(f"{module_name}.{class_name}.__init__", return_value=None)
        mocker.patch(f"{module_name}.{class_name}.clean_up", return_value=None)
    manager = manager_mod.AppManager()
    manager.events = mocker.Mock()
    return manager


class TestAppManagerInitialization:
    """Test AppManager initialization."""

    def test_init_is_working_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """All attributes and setting up exist."""
        mock_current_app = mocker.patch(
            "pireaderos.core.manager.current.CurrentApp"
        )
        mock_event_mgr = mocker.patch(
            "pireaderos.core.manager.event.EventManager"
        )
        mock_events_instance = mock_event_mgr.return_value
        mock_switch_app = mocker.patch(
            "pireaderos.core.manager.AppManager._switch_app"
        )

        manager = manager_mod.AppManager()

        mock_current_app.assert_called_once()
        assert manager.current is mock_current_app.return_value
        mock_event_mgr.assert_called_once()
        mock_events_instance.subscribe.assert_called_once_with(
            "switch_app", mock_switch_app
        )
        mock_switch_app.assert_called_once_with("HomeApp")


class TestAppManagerSwitchingApp:
    """Test AppManager switch_app."""

    def test_app_name_is_valid_with_different_existing_app_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_get_app_class: pytest_mock.MockType,
        mock_current_app_with: Callable[..., pytest_mock.MockType],
        mock_unload_app_module: pytest_mock.MockType,
        app_manager_unittest: manager_mod.AppManager,
    ) -> None:
        """Switch app successfully when a different app is already loaded."""
        mock_new_app_class = mocker.Mock()
        mock_get_app_class.return_value = mock_new_app_class  # new app class

        mock_current_instance = mock_current_app_with(
            mocker.Mock(), "OldAppName"
        )  # old app

        app_manager_unittest.current = mock_current_instance
        app_manager_unittest._switch_app("NewAppName")

        mock_get_app_class.assert_called_once_with("NewAppName")
        mock_current_instance.app.clean_up.assert_called_once()
        mock_unload_app_module.assert_called_once_with("OldAppName")
        mock_new_app_class.assert_called_once_with(app_manager_unittest.events)
        mock_current_instance.app_set.assert_called_once_with(
            mock_new_app_class.return_value, "NewAppName"
        )

    def test_app_name_is_valid_with_different_existing_app_integration(
        self, app_manager_integration: manager_mod.AppManager
    ) -> None:
        """Switch app successfully when a different app is already loaded."""
        app_manager_integration.current = current.CurrentApp()
        app_manager_integration.current._app = home.HomeApp(
            app_manager_integration.events
        )
        app_manager_integration.current._app_name = "HomeApp"
        app_manager_integration._switch_app("SettingsApp")

        assert isinstance(
            app_manager_integration.current.app, settings.SettingsApp
        )
        assert app_manager_integration.current.app_name == "SettingsApp"

    def test_app_name_is_valid_with_no_existing_app_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_get_app_class: pytest_mock.MockType,
        mock_current_app_with: Callable[..., pytest_mock.MockType],
        mock_unload_app_module: pytest_mock.MockType,
        app_manager_unittest: manager_mod.AppManager,
    ) -> None:
        """Switch app successfully when no app is loaded."""
        mock_new_app_class = mocker.Mock()
        mock_get_app_class.return_value = mock_new_app_class  # new app class

        mock_existing_app = mocker.Mock()
        mock_current_instance = mock_current_app_with(None, None)  # old app

        app_manager_unittest.current = mock_current_instance
        app_manager_unittest._switch_app("NewAppName")

        mock_get_app_class.assert_called_once_with("NewAppName")
        mock_existing_app.clean_up.assert_not_called()
        mock_unload_app_module.assert_not_called()
        mock_new_app_class.assert_called_once_with(app_manager_unittest.events)
        mock_current_instance.app_set.assert_called_once_with(
            mock_new_app_class.return_value, "NewAppName"
        )

    @pytest.mark.parametrize("app_name", registry.APP_REGISTRY.keys())
    def test_app_name_is_valid_with_no_existing_app_integration(
        self, app_manager_integration: manager_mod.AppManager, app_name: str
    ) -> None:
        """Switch app successfully when no app is loaded."""
        app_manager_integration.current = current.CurrentApp()
        app_manager_integration._switch_app(app_name)

        class_name = app_manager_integration.current.app.__class__.__name__
        assert class_name == app_name
        assert app_manager_integration.current.app_name == app_name

    def test_app_name_is_valid_with_same_existing_app_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_get_app_class: pytest_mock.MockType,
        mock_current_app_with: Callable[..., pytest_mock.MockType],
        mock_unload_app_module: pytest_mock.MockType,
        app_manager_unittest: manager_mod.AppManager,
    ) -> None:
        """Switch app successfully when the same app is already loaded."""
        mock_new_app_class = mocker.Mock()
        mock_get_app_class.return_value = mock_new_app_class  # new app class

        mock_existing_app = mocker.Mock()
        mock_existing_app.name = "OldAppName"
        mock_current_instance = mock_current_app_with(
            mock_existing_app, mock_existing_app.name
        )  # old app

        app_manager_unittest.current = mock_current_instance
        app_manager_unittest._switch_app("OldAppName")

        mock_get_app_class.assert_not_called()
        mock_existing_app.clean_up.assert_not_called()
        mock_unload_app_module.assert_not_called()
        mock_new_app_class.assert_not_called()
        mock_new_app_class.assert_not_called()
        mock_current_instance.app_set.assert_not_called()

        assert app_manager_unittest.current.app is mock_existing_app
        assert app_manager_unittest.current.app_name is mock_existing_app.name

    def test_app_name_is_valid_with_same_existing_app_integration(
        self, app_manager_integration: manager_mod.AppManager
    ) -> None:
        """Switch app successfully when the same app is already loaded."""
        app_manager_integration.current = current.CurrentApp()
        app_manager_integration.current._app = existing_app = home.HomeApp(
            app_manager_integration.events
        )
        app_manager_integration.current._app_name = existing_app_name = (
            "HomeApp"
        )
        app_manager_integration._switch_app("HomeApp")

        assert app_manager_integration.current.app is existing_app
        assert app_manager_integration.current.app_name is existing_app_name

    @pytest.mark.parametrize("app_name", ["", "InvalidApp", None, 1, object()])
    def test_app_name_is_invalid_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_get_app_class: pytest_mock.MockType,
        mock_current_app_with: Callable[..., pytest_mock.MockType],
        mock_unload_app_module: pytest_mock.MockType,
        app_manager_unittest: manager_mod.AppManager,
        app_name: object,
    ) -> None:
        """Switch app fails when app_name is not registered or a string."""
        mock_new_app_class = mocker.Mock()
        mock_get_app_class.return_value = None  # new app class

        mock_existing_app = mocker.Mock()
        mock_current_instance = mock_current_app_with(
            mock_existing_app, "HomeApp"
        )  # old app

        app_manager_unittest.current = mock_current_instance
        app_manager_unittest._switch_app(app_name)  # pyright: ignore[reportArgumentType]

        mock_get_app_class.assert_called_once_with(app_name)
        mock_existing_app.clean_up.assert_not_called()
        mock_unload_app_module.assert_not_called()
        mock_new_app_class.assert_not_called()
        mock_current_instance.app_set.assert_not_called()

    @pytest.mark.parametrize("app_name", ["", "InvalidApp", None, 1, object()])
    def test_app_name_is_invalid_integration(
        self, app_manager_integration: manager_mod.AppManager, app_name: object
    ) -> None:
        """Switch app fails when app_name is not registered or a string."""
        app_manager_integration.current = current.CurrentApp()
        app_manager_integration.current._app = existing_app = home.HomeApp(
            app_manager_integration.events
        )
        app_manager_integration.current._app_name = existing_app_name = (
            "HomeApp"
        )
        app_manager_integration._switch_app(app_name)  # pyright: ignore[reportArgumentType]

        assert app_manager_integration.current.app is existing_app
        assert app_manager_integration.current.app_name is existing_app_name


class TestAppManagerRun:
    """Test AppManager run."""

    def test_run_terminates_at_keyboard_interrupt_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        app_manager_unittest: manager_mod.AppManager,
        mock_current_app_with: Callable[..., pytest_mock.MockType],
    ) -> None:
        """Terminate run loop when the user hits Ctrl-c."""
        mocker.patch("time.sleep", side_effect=KeyboardInterrupt)
        mock_current_instance = mock_current_app_with(mocker.Mock(), "MockApp")
        app_manager_unittest.current = mock_current_instance

        app_manager_unittest.run()

    def test_run_terminates_when_no_app_is_loaded_unittest(
        self,
        app_manager_unittest: manager_mod.AppManager,
        mock_current_app_with: Callable[..., pytest_mock.MockType],
    ) -> None:
        """Terminate when there is no app loaded."""
        mock_current_instance = mock_current_app_with(None, None)
        app_manager_unittest.current = mock_current_instance

        with pytest.raises(AssertionError):
            app_manager_unittest.run()
