from pireaderos.core.manager import AppManager


class TestAppManagerInitialization:
    def test_init_is_working_unittest(self, mocker):
        MockCurrentApp = mocker.patch("pireaderos.core.manager.CurrentApp")
        MockSwitchApp = mocker.patch(
            "pireaderos.core.manager.AppManager._switch_app")

        manager = AppManager()

        MockCurrentApp.assert_called_once()
        assert manager.current is MockCurrentApp.return_value
        MockSwitchApp.assert_called_once_with("HomeApp")
