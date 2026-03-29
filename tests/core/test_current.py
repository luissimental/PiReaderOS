import pytest

from pireaderos.core.current import CurrentApp


class TestCurrentAppInitialization:
    def test_init_is_working_unittest(self):
        current = CurrentApp()
        assert current._app == None
        assert current._app_name == None


class TestCurrentAppProperties:
    @pytest.mark.parametrize("app", ["APP", "APP2", None])
    def test_app_property_is_working_unittest(self, app):
        current = CurrentApp()
        current._app = app
        assert current.app == app

    @pytest.mark.parametrize("app_name", ["APPNAME", "APPNAME2", None])
    def test_app_name_property_is_working_unittest(self, app_name):
        current = CurrentApp()
        current._app_name = app_name
        assert current.app_name == app_name

    @pytest.mark.parametrize("app, app_name", [
        ("APP", "APPNAME"), ("APP2", "APPNAME2"), (None, None)
    ])
    def test_app_set_is_working_unittest(self, app, app_name):
        current = CurrentApp()
        current.app_set(app, app_name)
        assert current.app == app
        assert current.app_name == app_name
