import pytest
from unittest.mock import call

from pireaderos.hardware.touch import TouchDriver, RST_PIN, INT_PIN


@pytest.fixture
def mock_touch_driver(mocker):
    mocker.patch.object(TouchDriver, "__init__", return_value=None)
    MockHM = mocker.patch("pireaderos.hal.manager.HardwareManager")

    driver = TouchDriver(mocker.Mock(), mocker.Mock())
    driver._hw = MockHM
    driver._closed = False
    driver._int_callback = mocker.Mock()

    driver._reset_pin = mocker.Mock()
    driver._int_pin = mocker.Mock()

    return driver


class TestTouchDriverInitialization:
    def test_init_is_working_unittest(self, mocker):
        MockHM = mocker.patch("pireaderos.hardware.touch.HardwareManager")
        MockGPIOPin = mocker.patch("pireaderos.hal.manager.GPIOPin")
        MockHM.request_pin.return_value = MockGPIOPin
        MockHWReset = mocker.patch.object(
            TouchDriver, "hardware_reset", return_value=None)

        driver = TouchDriver(MockHM, mocker.Mock())

        MockHM.request_pin.assert_has_calls([
            call(RST_PIN, mode="output"),
            call(INT_PIN, mode="input", pull_up=True)
        ])
        MockGPIOPin.set_when_activated.assert_called_once_with(
            driver._on_touch_interrupt)
        MockHWReset.assert_called_once()


class TestTouchDriverOnTouchInterrupt:
    def test_on_touch_interrupt_is_working_unittest(
        self, mocker, mock_touch_driver
    ):
        MockReadTch = mocker.patch.object(
            TouchDriver, "read_touches", return_value=None)

        mock_touch_driver._on_touch_interrupt()

        MockReadTch.assert_called_once()
        mock_touch_driver._int_callback.assert_called_once_with(
            MockReadTch.return_value)


class TestTouchDriverHardwareReset:
    def test_hardware_reset_is_working_unittest(self, mock_touch_driver):
        mock_touch_driver.hardware_reset()

        mock_touch_driver._reset_pin.off.assert_called_once()
        mock_touch_driver._reset_pin.on.assert_called_once()


class TestTouchDriverSetPowerMode:
    @pytest.mark.parametrize("mode", ["active", "monitor", "hibernate"])
    def test_set_power_mode_is_working_unittest(self, mock_touch_driver, mode):
        mock_touch_driver.set_power_mode(mode)

        mock_touch_driver._hw.i2c_write.assert_called_once()

    @pytest.mark.parametrize("mode", ["", "InvalidMode", 1, None])
    def test_set_power_mode_raises_exc_on_invalid_mode_unittest(
        self, mock_touch_driver, mode
    ):
        with pytest.raises(ValueError):
            mock_touch_driver.set_power_mode(mode)


class TestTouchDriverReadTouches:
    def test_read_one_touch_point_unittest(self, mock_touch_driver):
        mock_touch_driver._hw.i2c_read_byte_data.return_value = 1
        mock_touch_driver._hw.i2c_read_block_data.return_value = [
            0x01, 0x02, 0x03, 0x04, 0x05, 0x06]

        result = mock_touch_driver.read_touches()

        mock_touch_driver._hw.i2c_read_byte_data.assert_called_once()
        mock_touch_driver._hw.i2c_read_block_data.assert_called_once()
        assert isinstance(result, list)
        assert len(result) == 1
        assert len(result[0]) == 3

    def test_read_two_touch_points_unittest(self, mock_touch_driver):
        mock_touch_driver._hw.i2c_read_byte_data.return_value = 2
        mock_touch_driver._hw.i2c_read_block_data.return_value = [
            0x01, 0x02, 0x03, 0x04, 0x05, 0x06,
            0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C
        ]

        result = mock_touch_driver.read_touches()

        mock_touch_driver._hw.i2c_read_byte_data.assert_called_once()
        mock_touch_driver._hw.i2c_read_block_data.assert_called_once()
        assert isinstance(result, list)
        assert len(result) == 2
        assert len(result[0]) == 3
        assert len(result[1]) == 3

    def test_read_touches_returns_empty_list_if_no_touches_unittest(
        self, mock_touch_driver
    ):
        mock_touch_driver._hw.i2c_read_byte_data.return_value = 0

        result = mock_touch_driver.read_touches()

        mock_touch_driver._hw.i2c_read_byte_data.assert_called_once()
        mock_touch_driver._hw.i2c_read_block_data.assert_not_called()
        assert isinstance(result, list)
        assert result == []


class TestTouchDriverCleanUp:
    def test_clean_up_is_working_unittest(self, mock_touch_driver):
        mock_touch_driver.clean_up()

        mock_touch_driver._hw.release_pin.assert_has_calls([
            call(mock_touch_driver._reset_pin),
            call(mock_touch_driver._int_pin)
        ])


class TestTouchDriverAfterCleanUp:
    def test_hardware_reset_fails_after_clean_up_unittest(
        self, mock_touch_driver
    ):
        mock_touch_driver.clean_up()

        with pytest.raises(RuntimeError):
            mock_touch_driver.hardware_reset()

    def test_set_power_mode_fails_after_clean_up_unittest(
        self, mock_touch_driver
    ):
        mock_touch_driver.clean_up()

        with pytest.raises(RuntimeError):
            mock_touch_driver.set_power_mode("monitor")

    def test_read_touches_fails_after_clean_up_unittest(
        self, mock_touch_driver
    ):
        mock_touch_driver.clean_up()

        with pytest.raises(RuntimeError):
            mock_touch_driver.read_touches()
