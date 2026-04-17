import pytest

from pireaderos.core import current as current_mod


class TestCurrentAppInitialization:
    """Test CurrentApp initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        current = current_mod.CurrentApp()
        assert current._app is None
        assert current._app_name is None


class TestCurrentAppProperties:
    """Test CurrentApp properties."""

    @pytest.mark.parametrize("app", ["APP", "APP2", None])
    def test_app_property_is_working_unittest(self, app: str) -> None:
        """Test app property returns the app."""
        current = current_mod.CurrentApp()
        current._app = app  # pyright: ignore[reportAttributeAccessIssue]
        assert current.app == app

    @pytest.mark.parametrize("app_name", ["APPNAME", "APPNAME2", None])
    def test_app_name_property_is_working_unittest(
        self, app_name: object
    ) -> None:
        """Test app_name property returns the app name."""
        current = current_mod.CurrentApp()
        current._app_name = app_name  # pyright: ignore[reportAttributeAccessIssue]
        assert current.app_name == app_name

    @pytest.mark.parametrize(
        "app, app_name",
        [("APP", "APPNAME"), ("APP2", "APPNAME2"), (None, None)],
    )
    def test_app_set_is_working_unittest(
        self, app: object, app_name: object
    ) -> None:
        """Test app_set properly sets the attributes."""
        current = current_mod.CurrentApp()
        current.app_set(app, app_name)  # pyright: ignore[reportArgumentType]
        assert current.app == app
        assert current.app_name == app_name
