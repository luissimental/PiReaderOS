from unittest import mock

import pytest
import pytest_mock

from pireaderos.hardware import models, touch


@pytest.fixture
def mock_touch_driver(mocker: pytest_mock.MockerFixture) -> touch.TouchDriver:
    """Mock TouchDriver __init__ and attributes."""
    mocker.patch.object(touch.TouchDriver, "__init__", return_value=None)
    mock_hm = mocker.patch("pireaderos.hal.manager.HardwareManager")

    driver = touch.TouchDriver(mocker.Mock(), mocker.Mock())
    driver._hw = mock_hm
    driver._closed = False
    driver._interrupt_callback = mocker.Mock()

    driver._reset_pin = mocker.Mock()
    driver._int_pin = mocker.Mock()

    return driver


class TestTouchDriverInitialization:
    """Test TouchDriver initialization."""

    def test_init_is_working_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Calls are present."""
        mock_hm = mocker.patch(
            "pireaderos.hardware.touch.manager.HardwareManager"
        )
        mock_gpio_pin = mocker.patch("pireaderos.hal.manager.GPIOPin")
        mock_hm.request_pin.return_value = mock_gpio_pin
        mock_hw_reset = mocker.patch.object(
            touch.TouchDriver, "hardware_reset", return_value=None
        )

        driver = touch.TouchDriver(mock_hm, mocker.Mock())

        mock_hm.request_pin.assert_has_calls(
            [
                mock.call(touch.RST_PIN, mode="output"),
                mock.call(touch.INT_PIN, mode="input", pull_up=True),
            ]
        )
        mock_gpio_pin.set_when_activated.assert_called_once_with(
            driver._on_touch_interrupt
        )
        mock_hw_reset.assert_called_once()


class TestTouchDriverOnTouchInterrupt:
    """Test TouchDriver on_touch_interrupt."""

    def test_on_touch_interrupt_is_working_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_touch_driver: pytest_mock.MockType,
    ) -> None:
        """Calls are present."""
        mock_read_touches = mocker.patch.object(
            touch.TouchDriver, "read_touches", return_value=None
        )

        mock_touch_driver._on_touch_interrupt()

        mock_read_touches.assert_called_once()
        mock_touch_driver._interrupt_callback.assert_called_once_with(
            mock_read_touches.return_value
        )


class TestTouchDriverHardwareReset:
    """Test TouchDriver hardware_reset."""

    def test_hardware_reset_is_working_unittest(
        self, mock_touch_driver: pytest_mock.MockType
    ) -> None:
        """Calls are present."""
        mock_touch_driver.hardware_reset()

        mock_touch_driver._reset_pin.off.assert_called_once()
        mock_touch_driver._reset_pin.on.assert_called_once()


class TestTouchDriverSetPowerMode:
    """Test TouchDriver set_power_mode."""

    @pytest.mark.parametrize("mode", ["active", "monitor", "hibernate"])
    def test_set_power_mode_is_working_unittest(
        self, mock_touch_driver: pytest_mock.MockType, mode: str
    ) -> None:
        """Calls are present."""
        mock_touch_driver.set_power_mode(mode)

        mock_touch_driver._hw.i2c_write.assert_called_once()

    @pytest.mark.parametrize("mode", ["", "InvalidMode", 1, None])
    def test_set_power_mode_raises_exc_on_invalid_mode_unittest(
        self, mock_touch_driver: pytest_mock.MockType, mode: object
    ) -> None:
        """Raise error on invalid mode."""
        with pytest.raises(ValueError):
            mock_touch_driver.set_power_mode(mode)


class TestTouchDriverReadTouches:
    """Test TouchDriver read_touches."""

    def test_read_one_touch_point_unittest(
        self, mock_touch_driver: pytest_mock.MockType
    ) -> None:
        """Return touch data for one finger."""
        mock_touch_driver._hw.i2c_read_byte_data.return_value = 1
        mock_touch_driver._hw.i2c_read_block_data.return_value = [
            0x01,
            0x02,
            0x03,
            0x04,
            0x05,
            0x06,
        ]

        result = mock_touch_driver.read_touches()

        mock_touch_driver._hw.i2c_read_byte_data.assert_called_once()
        mock_touch_driver._hw.i2c_read_block_data.assert_called_once()
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], models.TouchPoint)

    def test_read_two_touch_points_unittest(
        self, mock_touch_driver: pytest_mock.MockType
    ) -> None:
        """Return touch data for two fingers."""
        mock_touch_driver._hw.i2c_read_byte_data.return_value = 2
        mock_touch_driver._hw.i2c_read_block_data.return_value = [
            0x01,
            0x02,
            0x03,
            0x04,
            0x05,
            0x06,
            0x07,
            0x08,
            0x09,
            0x0A,
            0x0B,
            0x0C,
        ]

        result = mock_touch_driver.read_touches()

        mock_touch_driver._hw.i2c_read_byte_data.assert_called_once()
        mock_touch_driver._hw.i2c_read_block_data.assert_called_once()
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], models.TouchPoint)
        assert isinstance(result[1], models.TouchPoint)

    def test_read_touches_returns_empty_list_if_no_touches_unittest(
        self, mock_touch_driver: pytest_mock.MockType
    ) -> None:
        """Return empty list on no touch events."""
        mock_touch_driver._hw.i2c_read_byte_data.return_value = 0

        result = mock_touch_driver.read_touches()

        mock_touch_driver._hw.i2c_read_byte_data.assert_called_once()
        mock_touch_driver._hw.i2c_read_block_data.assert_not_called()
        assert isinstance(result, list)
        assert result == []


class TestTouchDriverCleanUp:
    """Test TouchDriver clean_up."""

    def test_clean_up_is_working_unittest(
        self, mock_touch_driver: pytest_mock.MockType
    ) -> None:
        """Calls are present."""
        mock_touch_driver.clean_up()

        mock_touch_driver._hw.release_pin.assert_has_calls(
            [
                mock.call(mock_touch_driver._reset_pin),
                mock.call(mock_touch_driver._int_pin),
            ]
        )


class TestTouchDriverAfterCleanUp:
    """Test TouchDriver after clean_up."""

    def test_hardware_reset_fails_after_clean_up_unittest(
        self, mock_touch_driver: pytest_mock.MockType
    ) -> None:
        """Raise error when trying to hardware_reset."""
        mock_touch_driver.clean_up()

        with pytest.raises(RuntimeError):
            mock_touch_driver.hardware_reset()

    def test_set_power_mode_fails_after_clean_up_unittest(
        self, mock_touch_driver: pytest_mock.MockType
    ) -> None:
        """Raise error when trying to set_power_mode."""
        mock_touch_driver.clean_up()

        with pytest.raises(RuntimeError):
            mock_touch_driver.set_power_mode("monitor")

    def test_read_touches_fails_after_clean_up_unittest(
        self, mock_touch_driver: pytest_mock.MockType
    ) -> None:
        """Raise error when trying to clean_up."""
        mock_touch_driver.clean_up()

        with pytest.raises(RuntimeError):
            mock_touch_driver.read_touches()
