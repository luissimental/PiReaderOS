import sys

import pytest
import pytest_mock

from pireaderos.apps import registry


@pytest.fixture
def mock_module(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock a generic module."""
    mock = mocker.Mock()
    mock.ClassName = "returns_classname"
    return mock


@pytest.fixture
def mock_import_module(
    mocker: pytest_mock.MockerFixture,
) -> pytest_mock.MockType:
    """Mock the importlib.import_module function."""
    return mocker.patch("pireaderos.apps.registry.importlib.import_module")


@pytest.fixture
def app_registry_single() -> dict[str, str]:
    """Mock a registry dict."""
    return {"ClassName": "app.module"}


class TestGetAppClassFunction:
    """Test get_app_class."""

    def test_app_class_is_valid_unittest(
        self,
        mock_module: pytest_mock.MockType,
        mock_import_module: pytest_mock.MockType,
        app_registry_single: dict[str, str],
    ) -> None:
        """Return the class when app_class is valid."""
        mock_import_module.return_value = mock_module
        result = registry.get_app_class("ClassName", app_registry_single)

        mock_import_module.assert_called_once_with("app.module")
        assert result == "returns_classname"

    @pytest.mark.parametrize("app_class", registry.APP_REGISTRY.keys())
    def test_app_class_is_valid_integration(self, app_class: str) -> None:
        """Return the class when app_class is valid."""
        result = registry.get_app_class(app_class)
        assert result is not None
        assert result.__name__ == app_class

    @pytest.mark.parametrize("app_class", [None, 1, object()])
    def test_app_class_is_not_str_type_unittest(
        self,
        mock_module: pytest_mock.MockType,
        mock_import_module: pytest_mock.MockType,
        app_registry_single: dict[str, str],
        app_class: object,
    ) -> None:
        """Return None when app_class is not a string."""
        mock_import_module.return_value = mock_module
        result = registry.get_app_class(app_class, app_registry_single)  # pyright: ignore[reportArgumentType]

        mock_import_module.assert_not_called()
        assert result is None

    @pytest.mark.parametrize("app_class", [None, 1, object()])
    def test_app_class_is_not_str_type_integration(
        self, app_class: object
    ) -> None:
        """Return None when app_class is not a string."""
        result = registry.get_app_class(app_class)  # pyright: ignore[reportArgumentType]
        assert result is None

    @pytest.mark.parametrize("app_class", ["", "InvalidApp"])
    def test_app_class_is_missing_in_app_registry_unittest(
        self,
        mock_module: pytest_mock.MockType,
        mock_import_module: pytest_mock.MockType,
        app_registry_single: dict[str, str],
        app_class: str,
    ) -> None:
        """Return None when app_class is not in the registry."""
        mock_import_module.return_value = mock_module
        result = registry.get_app_class(app_class, app_registry_single)

        mock_import_module.assert_not_called()
        assert result is None

    @pytest.mark.parametrize("app_class", ["", "InvalidApp"])
    def test_app_class_is_missing_in_app_registry_integration(
        self, app_class: str
    ) -> None:
        """Return None when app_class is not in the registry."""
        result = registry.get_app_class(app_class)
        assert result is None

    def test_app_class_cannot_import_module_unittest(
        self,
        mock_import_module: pytest_mock.MockType,
        app_registry_single: dict[str, str],
    ) -> None:
        """Return None when app_class in registry but cannot import module."""
        mock_import_module.side_effect = ModuleNotFoundError
        result = registry.get_app_class("ClassName", app_registry_single)

        mock_import_module.assert_called_once_with("app.module")
        assert result is None

    def test_app_class_cannot_import_module_integration(
        self, app_registry_single: dict[str, str]
    ) -> None:
        """Return None when app_class in registry but cannot import module."""
        result = registry.get_app_class("ClassName", app_registry_single)
        assert result is None

    def test_app_class_cannot_getattr_from_module_unittest(
        self,
        mock_import_module: pytest_mock.MockType,
        app_registry_single: dict[str, str],
    ) -> None:
        """Return None.

        App_class is in registry and can import module, but cannot get class.
        """
        mock_import_module.return_value = None
        result = registry.get_app_class("ClassName", app_registry_single)

        mock_import_module.assert_called_once_with("app.module")
        assert result is None

    def test_app_class_cannot_getattr_from_module_integration(self) -> None:
        """Return None.

        App_class is in registry and can import module, but cannot get class.
        """
        app_reg = {"InvalidClass": "pireaderos.apps.home"}
        result = registry.get_app_class("InvalidClass", app_reg)
        assert result is None


class TestUnloadAppModuleFunction:
    """Test unload_app_module."""

    def test_app_class_is_valid_unittest(
        self,
        monkeypatch: pytest.MonkeyPatch,
        app_registry_single: dict[str, str],
    ) -> None:
        """Remove module successfully."""
        monkeypatch.setitem(sys.modules, "app.module", "ClassName")
        assert "app.module" in sys.modules

        result = registry.unload_app_module("ClassName", app_registry_single)
        assert "app.module" not in sys.modules
        assert result is True

    @pytest.mark.parametrize(
        "app_class, module_name", registry.APP_REGISTRY.items()
    )
    def test_app_class_is_valid_integration(
        self, monkeypatch: pytest.MonkeyPatch, app_class: str, module_name: str
    ) -> None:
        """Remove module successfully."""
        monkeypatch.setitem(sys.modules, module_name, "HomeApp")
        assert module_name in sys.modules

        result = registry.unload_app_module(app_class)
        assert module_name not in sys.modules
        assert result is True

    @pytest.mark.parametrize("app_class", [None, 1, object()])
    def test_app_class_is_not_str_type_unittest(
        self,
        monkeypatch: pytest.MonkeyPatch,
        app_registry_single: dict[str, str],
        app_class: object,
    ) -> None:
        """Remove module fails when app_class is not a string."""
        monkeypatch.setitem(sys.modules, "app.module", "ClassName")
        assert "app.module" in sys.modules

        result = registry.unload_app_module(app_class, app_registry_single)  # pyright: ignore[reportArgumentType]
        assert "app.module" in sys.modules
        assert result is False

    @pytest.mark.parametrize("app_class", [None, 1, object()])
    def test_app_class_is_not_str_type_integration(
        self, app_class: object
    ) -> None:
        """Remove module fails when app_class is not a string."""
        result = registry.unload_app_module(app_class)  # pyright: ignore[reportArgumentType]
        assert result is False

    @pytest.mark.parametrize("app_class", ["", "InvalidClass"])
    def test_app_class_is_missing_in_app_registry_unittest(
        self,
        monkeypatch: pytest.MonkeyPatch,
        app_registry_single: dict[str, str],
        app_class: str,
    ) -> None:
        """Remove module fails when app_class is not in registry."""
        monkeypatch.setitem(sys.modules, "app.module", "ClassName")
        assert "app.module" in sys.modules

        result = registry.unload_app_module(app_class, app_registry_single)
        assert "app.module" in sys.modules
        assert result is False

    @pytest.mark.parametrize("app_class", ["", "InvalidClass"])
    def test_app_class_is_missing_in_app_registry_integration(
        self, app_class: str
    ) -> None:
        """Remove module fails when app_class is not in registry."""
        result = registry.unload_app_module(app_class)
        assert result is False

    def test_app_class_is_valid_but_missing_in_sys_modules_unittest(
        self, app_registry_single: dict[str, str]
    ) -> None:
        """Remove module fails.

        App_class is in registry but module is not imported.
        """
        assert "app.module" not in sys.modules

        result = registry.unload_app_module("ClassName", app_registry_single)
        assert "app.module" not in sys.modules
        assert result is False

    @pytest.mark.parametrize(
        "app_class, module_name", registry.APP_REGISTRY.items()
    )
    def test_app_class_is_valid_but_missing_in_sys_modules_integration(
        self, monkeypatch: pytest.MonkeyPatch, app_class: str, module_name: str
    ) -> None:
        """Remove module fails.

        App_class is in registry but module is not imported.
        """
        monkeypatch.delitem(sys.modules, module_name, raising=False)
        assert module_name not in sys.modules

        result = registry.unload_app_module(app_class)
        assert module_name not in sys.modules
        assert result is False
