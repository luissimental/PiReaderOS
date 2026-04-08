import pytest
from unittest.mock import call

from pireaderos.hal.manager import HardwareManager


@pytest.fixture
def mock_smbus(mocker):
    return mocker.patch("pireaderos.hal.manager.smbus2.SMBus")


@pytest.fixture
def mock_digital_input(mocker):
    return mocker.patch("pireaderos.hal.manager.DigitalInputDevice")


@pytest.fixture
def mock_digital_output(mocker):
    return mocker.patch("pireaderos.hal.manager.DigitalOutputDevice")


@pytest.fixture
def mock_hardware_manager(
    mock_smbus, mock_digital_input, mock_digital_output
):
    return HardwareManager()


class TestHardwareManagerInitialization:
    def test_init_is_working_unittest(self, mock_smbus):
        HardwareManager()
        mock_smbus.assert_called_once_with(3)


class TestHardwareManagerAsContextManager:
    def test_hardware_manager_is_proper_context_manager_unittest(
        self, mocker, mock_hardware_manager
    ):
        spy_enter = mocker.spy(HardwareManager, "__enter__")
        spy_exit = mocker.spy(HardwareManager, "__exit__")
        spy_clean_up = mocker.spy(HardwareManager, "clean_up")

        with mock_hardware_manager:
            spy_clean_up.assert_not_called()
            spy_exit.assert_not_called()

        spy_enter.assert_called_once()
        spy_exit.assert_called_once()
        spy_clean_up.assert_called_once()


class TestHardwareManagerRequestPin:
    def test_request_input_pin_unittest(
        self, mock_digital_input, mock_digital_output, mock_hardware_manager
    ):
        pin = mock_hardware_manager.request_pin(17, "input")

        mock_digital_input.assert_called_once_with(17)
        mock_digital_output.assert_not_called()
        assert pin.pin_number == 17
        assert pin._device == mock_digital_input.return_value

    def test_request_output_pin_unittest(
        self, mock_digital_input, mock_digital_output, mock_hardware_manager
    ):
        pin = mock_hardware_manager.request_pin(17, "output")

        mock_digital_output.assert_called_once_with(17)
        mock_digital_input.assert_not_called()
        assert pin.pin_number == 17
        assert pin._device == mock_digital_output.return_value

    def test_request_invalid_mode_unittest(
        self, mock_digital_input, mock_digital_output, mock_hardware_manager
    ):
        with pytest.raises(ValueError):
            mock_hardware_manager.request_pin(17, "InvalidMode")

        mock_digital_input.assert_not_called()
        mock_digital_output.assert_not_called()

    def test_duplicate_request_input_pin_unittest(self, mock_hardware_manager):
        mock_hardware_manager.request_pin(17, "input")

        with pytest.raises(RuntimeError):
            mock_hardware_manager.request_pin(17, "input")

    def test_duplicate_request_output_pin_unittest(self, mock_hardware_manager):
        mock_hardware_manager.request_pin(17, "output")

        with pytest.raises(RuntimeError):
            mock_hardware_manager.request_pin(17, "output")

    def test_multiple_different_request_input_pin_unittest(
        self, mock_digital_input, mock_digital_output, mock_hardware_manager
    ):
        pin1 = mock_hardware_manager.request_pin(17, "input")
        pin2 = mock_hardware_manager.request_pin(18, "input")

        mock_digital_input.assert_has_calls(
            [call(17), call(18)], any_order=False)
        mock_digital_output.assert_not_called()
        assert pin1.pin_number == 17
        assert pin1._device == mock_digital_input.return_value
        assert pin2.pin_number == 18
        assert pin2._device == mock_digital_input.return_value

    def test_multiple_different_request_output_pin_unittest(
        self, mock_digital_input, mock_digital_output, mock_hardware_manager
    ):
        pin1 = mock_hardware_manager.request_pin(17, "output")
        pin2 = mock_hardware_manager.request_pin(18, "output")

        mock_digital_input.assert_not_called()
        mock_digital_output.assert_has_calls(
            [call(17), call(18)], any_order=False)
        assert pin1.pin_number == 17
        assert pin1._device == mock_digital_output.return_value
        assert pin2.pin_number == 18
        assert pin2._device == mock_digital_output.return_value

    def test_multiple_different_request_input_or_output_pin_unittest(
        self, mock_digital_input, mock_digital_output, mock_hardware_manager
    ):
        pin1 = mock_hardware_manager.request_pin(17, "input")
        pin2 = mock_hardware_manager.request_pin(18, "output")

        mock_digital_input.assert_called_once_with(17)
        mock_digital_output.assert_called_once_with(18)
        assert pin1.pin_number == 17
        assert pin1._device == mock_digital_input.return_value
        assert pin2.pin_number == 18
        assert pin2._device == mock_digital_output.return_value


class TestHardwareManagerReleasePin:
    def test_release_existing_pin_unittest(self, mocker, mock_hardware_manager):
        pin = mock_hardware_manager.request_pin(17, "input")
        pin_spy_close = mocker.spy(pin, "_close")

        mock_hardware_manager.release_pin(pin)

        pin_spy_close.assert_called_once()

    def test_release_existing_pin_with_many_requested_unittest(
        self, mocker, mock_hardware_manager
    ):
        pin1 = mock_hardware_manager.request_pin(17, "input")
        pin2 = mock_hardware_manager.request_pin(18, "input")
        pin1_spy_close = mocker.spy(pin1, "_close")
        pin2_spy_close = mocker.spy(pin2, "_close")

        mock_hardware_manager.release_pin(pin1)

        pin1_spy_close.assert_called_once()
        pin2_spy_close.assert_not_called()

    def test_release_already_released_pin_unittest(self, mock_hardware_manager):
        pin = mock_hardware_manager.request_pin(17, "input")

        mock_hardware_manager.release_pin(pin)

        with pytest.raises(RuntimeError):
            mock_hardware_manager.release_pin(pin)


class TestHardwareManagerI2CReadByteData:
    def test_i2c_read_returns_byte_unittest(self, mocker, mock_smbus):
        mock_smbus_instance = mocker.Mock()
        mock_smbus_instance.read_byte_data.return_value = 0x45
        mock_smbus.return_value = mock_smbus_instance

        hw = HardwareManager()
        result = hw.i2c_read_byte_data(0x38, 0x01)

        mock_smbus_instance.read_byte_data.assert_called_once_with(0x38, 0x01)
        assert result == 0x45


class TestHardwareManagerI2CReadBlockData:
    def test_i2c_read_returns_list_of_bytes_unittest(self, mocker, mock_smbus):
        mock_smbus_instance = mocker.Mock()
        mock_smbus_instance.read_i2c_block_data.return_value = [
            0x45, 0x46, 0x50]
        mock_smbus.return_value = mock_smbus_instance

        hw = HardwareManager()
        result = hw.i2c_read_block_data(0x38, 0x01, 3)

        mock_smbus_instance.read_i2c_block_data.assert_called_once_with(
            0x38, 0x01, 3)
        assert result == [0x45, 0x46, 0x50]

    def test_i2c_read_fails_when_length_is_invalid_unittest(
        self, mocker, mock_smbus, mock_hardware_manager
    ):
        mock_smbus_instance = mocker.Mock()
        mock_smbus_instance.read_i2c_block_data.return_value = [
            0x45, 0x46, 0x50]
        mock_smbus.return_value = mock_smbus_instance

        with pytest.raises(ValueError):
            mock_hardware_manager.i2c_read_block_data(0x38, 0x01, 0)


class TestHardwareManagerI2CWrite:
    def test_i2c_writes_one_byte_unittest(
        self, mock_smbus, mock_hardware_manager
    ):
        mock_hardware_manager.i2c_write(0x38, 0x02, 0x45)

        mock_smbus.return_value.write_byte_data.assert_called_once_with(
            0x38, 0x02, 0x45)

    def test_i2c_writes_list_of_bytes_unittest(
        self, mock_smbus, mock_hardware_manager
    ):
        mock_hardware_manager.i2c_write(0x38, 0x02, [0x45, 0x50, 0x12])

        mock_smbus.return_value.write_block_data.assert_called_once_with(
            0x38, 0x02, [0x45, 0x50, 0x12])


class TestHardwareManagerCleanUp:
    def test_clean_up_is_working_unittest(
        self, mocker, mock_smbus, mock_hardware_manager
    ):
        MockGPIO1 = mocker.Mock()
        MockGPIO2 = mocker.Mock()
        MockGPIO3 = mocker.Mock()

        mock_hardware_manager._active_pins = {
            1: MockGPIO1, 2: MockGPIO2, 3: MockGPIO3}

        mock_hardware_manager.clean_up()

        MockGPIO1._close.assert_called_once()
        MockGPIO2._close.assert_called_once()
        MockGPIO3._close.assert_called_once()
        mock_smbus.return_value.close.assert_called_once()
        assert not mock_hardware_manager._active_pins


class TestHardwareManagerAfterCleanUp:
    def test_request_pin_fails_after_clean_up_unittest(
        self, mock_digital_input, mock_hardware_manager
    ):
        mock_hardware_manager.clean_up()

        with pytest.raises(RuntimeError):
            mock_hardware_manager.request_pin(16, "input")

        mock_digital_input.assert_not_called()

    def test_release_pin_fails_after_clean_up_unittest(
        self, mock_hardware_manager
    ):
        pin = mock_hardware_manager.request_pin(16, "input")
        mock_hardware_manager.clean_up()

        with pytest.raises(RuntimeError):
            mock_hardware_manager.release_pin(pin)

    def test_i2c_read_byte_fails_after_clean_up_unittest(
        self, mock_hardware_manager
    ):
        mock_hardware_manager.clean_up()

        with pytest.raises(RuntimeError):
            mock_hardware_manager.i2c_read_byte_data(0x38, 0x01)

    def test_i2c_read_block_fails_after_clean_up_unittest(
        self, mock_hardware_manager
    ):
        mock_hardware_manager.clean_up()

        with pytest.raises(RuntimeError):
            mock_hardware_manager.i2c_read_block_data(0x38, 0x01, 2)

    def test_i2c_write_fails_after_clean_up_unittest(
        self, mock_hardware_manager
    ):
        mock_hardware_manager.clean_up()

        with pytest.raises(RuntimeError):
            mock_hardware_manager.i2c_write(0x38, 0x01, 0x45)
