from unittest import mock

import pytest
import pytest_mock
from PIL import Image

from pireaderos.hal import manager
from pireaderos.hardware import epaper


@pytest.fixture
def mock_epaper_driver(
    mocker: pytest_mock.MockerFixture,
) -> epaper.EPaperDriver:
    """Mock EPaperDriver dependencies."""
    mock_hm = mocker.patch(
        "pireaderos.hardware.epaper.manager.HardwareManager"
    )

    display = epaper.EPaperDriver(mock_hm)
    display._reset_pin = mocker.Mock()
    display._dc_pin = mocker.Mock()
    display._busy_pin = mocker.Mock()

    return display


@pytest.fixture
def mock_epaper_driver_spi(
    mocker: pytest_mock.MockerFixture,
) -> epaper.EPaperDriver:
    """Mock EPaperDriver dependencies and spi methods."""
    mock_hm = mocker.patch(
        "pireaderos.hardware.epaper.manager.HardwareManager"
    )

    display = epaper.EPaperDriver(mock_hm)
    display._reset_pin = mocker.Mock()
    display._dc_pin = mocker.Mock()
    display._busy_pin = mocker.Mock()

    mocker.patch.object(display, "_send_command", return_value=None)
    mocker.patch.object(display, "_send_byte", return_value=None)
    mocker.patch.object(display, "_send_block", return_value=None)
    mocker.patch.object(display, "_wait_on_busy", return_value=None)

    return display


class TestEPaperDriverInitialization:
    """Test EPaperDriver initialization."""

    def test_init_is_working_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """All attributes are present."""
        mock_hm = mocker.Mock()
        display = epaper.EPaperDriver(mock_hm)

        assert display._hw is mock_hm
        assert display._is_screen_on is False
        assert isinstance(display._width, int)
        assert isinstance(display._height, int)
        assert isinstance(display._width_bytes, int)
        assert isinstance(display._buffer_size, int)
        assert isinstance(display._previous_frame, bytearray)
        assert isinstance(display._current_frame, bytearray)


class TestEPaperDriverEnableHardware:
    """Test EPaperDriver _enable_hardware."""

    def test_enable_works_when_display_is_off_unittest(
        self, mock_epaper_driver: pytest_mock.MockType
    ) -> None:
        """Enable hardware when the display is off."""
        mock_epaper_driver._is_screen_on = False
        mock_epaper_driver._enable_hardware()

        mock_epaper_driver._hw.enable_spi.assert_called_once()
        mock_epaper_driver._hw.request_pin.assert_has_calls(
            [
                mock.call(epaper.PINS.RESET, "output"),
                mock.call(epaper.PINS.DC, "output"),
                mock.call(epaper.PINS.BUSY, "input"),
            ]
        )
        assert mock_epaper_driver._is_screen_on

    def test_enable_does_not_work_when_display_is_on_unittest(
        self, mock_epaper_driver: pytest_mock.MockType
    ) -> None:
        """Does not enable when the display is on."""
        mock_epaper_driver._is_screen_on = True
        mock_epaper_driver._enable_hardware()

        mock_epaper_driver._hw.enable_spi.assert_not_called()
        mock_epaper_driver._hw.request_pin.assert_not_called()
        assert mock_epaper_driver._is_screen_on


class TestEPaperDriverCloseHardware:
    """Test EPaperDriver _close_hardware."""

    def test_close_works_when_display_is_on_unittest(
        self, mock_epaper_driver: pytest_mock.MockType
    ) -> None:
        """Close hardware when the display is on."""
        mock_epaper_driver._is_screen_on = True
        mock_epaper_driver._close_hardware()

        mock_epaper_driver._hw.close_spi.assert_called_once()
        mock_epaper_driver._hw.release_pin.assert_has_calls(
            [
                mock.call(mock_epaper_driver._reset_pin),
                mock.call(mock_epaper_driver._dc_pin),
                mock.call(mock_epaper_driver._busy_pin),
            ]
        )
        assert not mock_epaper_driver._is_screen_on

    def test_close_does_not_work_when_display_is_off_unittest(
        self, mock_epaper_driver: pytest_mock.MockType
    ) -> None:
        """Does not close hardware when the display is off."""
        mock_epaper_driver._is_screen_on = False
        mock_epaper_driver._close_hardware()

        mock_epaper_driver._hw.close_spi.assert_not_called()
        mock_epaper_driver._hw.release_pin.assert_not_called()
        assert not mock_epaper_driver._is_screen_on


class TestEPaperDriverResetDisplay:
    """Test EPaperDriver _reset_display."""

    def test_reset_works_when_display_is_on_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver: pytest_mock.MockType,
    ) -> None:
        """Reset when the display is on."""
        mock_sleep = mocker.patch("time.sleep")
        mock_epaper_driver._is_screen_on = True
        mock_epaper_driver._reset_display()

        mock_epaper_driver._reset_pin.assert_has_calls(
            [mock.call.on, mock.call.off, mock.call.on]
        )
        mock_sleep.assert_has_calls(
            [mock.call(0.02), mock.call(0.002), mock.call(0.02)]
        )

    def test_reset_does_not_work_when_display_is_off_unittest(
        self, mock_epaper_driver: pytest_mock.MockType
    ) -> None:
        """Does not reset when the display is off."""
        mock_epaper_driver._is_screen_on = False
        mock_epaper_driver._reset_display()

        mock_epaper_driver._reset_pin.on.assert_not_called()
        mock_epaper_driver._reset_pin.off.assert_not_called()


class TestEPaperDriverWaitOnBusy:
    """Test EPaperDriver _wait_on_busy."""

    def test_wait_blocks_when_busy_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver: pytest_mock.MockType,
    ) -> None:
        """Block while the busy pin is active."""
        mock_sleep = mocker.patch("time.sleep")
        mock_is_active = mocker.patch.object(
            manager.GPIOPin,
            "is_active",
            new_callable=mocker.PropertyMock,
            side_effect=[True, True, False],
        )
        mock_epaper_driver._is_screen_on = True
        mock_epaper_driver._busy_pin = manager.GPIOPin(
            mocker.Mock(), mocker.Mock()
        )

        mock_epaper_driver._wait_on_busy()

        assert mock_is_active.call_count == 3
        assert mock_sleep.call_count == 3

    def test_wait_does_not_block_when_display_is_off_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver: pytest_mock.MockType,
    ) -> None:
        """Does not block when the display is off."""
        mock_sleep = mocker.patch("time.sleep")
        mock_epaper_driver._is_screen_on = False

        mock_epaper_driver._wait_on_busy()

        mock_sleep.assert_not_called()


class TestEPaperDriverSendCommand:
    """Test EPaperDriver _send_command."""

    def test_send_works_when_display_is_on_unittest(
        self, mock_epaper_driver: pytest_mock.MockType
    ) -> None:
        """Send command when the display is on."""
        mock_epaper_driver._is_screen_on = True

        mock_epaper_driver._send_command(0x01)

        mock_epaper_driver._dc_pin.off.assert_called_once()
        mock_epaper_driver._hw.spi_writebytes.assert_called_once_with([0x01])

    def test_send_does_not_work_when_display_is_off_unittest(
        self, mock_epaper_driver: pytest_mock.MockType
    ) -> None:
        """Does not send command when the display is off."""
        mock_epaper_driver._is_screen_on = False

        mock_epaper_driver._send_command(0x01)

        mock_epaper_driver._dc_pin.off.assert_not_called()
        mock_epaper_driver._hw.spi_writebytes.assert_not_called()


class TestEPaperDriverSendByte:
    """Test EPaperDriver _send_byte."""

    def test_send_works_when_display_is_on_unittest(
        self, mock_epaper_driver: pytest_mock.MockType
    ) -> None:
        """Send byte when the diplay is on."""
        mock_epaper_driver._is_screen_on = True

        mock_epaper_driver._send_byte(0x02)

        mock_epaper_driver._dc_pin.on.assert_called_once()
        mock_epaper_driver._hw.spi_writebytes.assert_called_once_with([0x02])

    def test_send_does_not_work_when_display_is_off_unittest(
        self, mock_epaper_driver: pytest_mock.MockType
    ) -> None:
        """Does not send byte when the display is off."""
        mock_epaper_driver._is_screen_on = False

        mock_epaper_driver._send_byte(0x02)

        mock_epaper_driver._dc_pin.on.assert_not_called()
        mock_epaper_driver._hw.spi_writebytes.assert_not_called()


class TestEPaperDriverSendBlock:
    """Test EPaperDriver _send_block."""

    def test_send_works_when_display_is_on_unittest(
        self, mock_epaper_driver: pytest_mock.MockType
    ) -> None:
        """Send block when the display is on."""
        mock_epaper_driver._is_screen_on = True

        mock_epaper_driver._send_block(bytearray(0x03))

        mock_epaper_driver._dc_pin.on.assert_called_once()
        mock_epaper_driver._hw.spi_writebytes2.assert_called_once_with(
            bytearray(0x03)
        )

    def test_send_does_not_work_when_display_is_off_unittest(
        self, mock_epaper_driver: pytest_mock.MockType
    ) -> None:
        """Does not send block when the display is off."""
        mock_epaper_driver._is_screen_on = False

        mock_epaper_driver._send_block(bytearray(0x03))

        mock_epaper_driver._dc_pin.on.assert_not_called()
        mock_epaper_driver._hw.spi_writebytes2.assert_not_called()


class TestEPaperDriverSetDisplayWindow:
    """Test EPaperDriver _set_display_window."""

    def test_set_works_when_display_is_on_unittest(
        self, mock_epaper_driver_spi: pytest_mock.MockType
    ) -> None:
        """Set display window when the display is on."""
        mock_epaper_driver_spi._width = 20
        mock_epaper_driver_spi._height = 20
        mock_epaper_driver_spi._is_screen_on = True

        mock_epaper_driver_spi._set_display_window(x=10, y=20, w=50, h=30)

        mock_epaper_driver_spi._send_command.assert_has_calls(
            [
                mock.call(epaper.COMMANDS.DATA_ENTRY_MODE_SETTING),
                mock.call(
                    epaper.COMMANDS.SET_RAM_X_ADDRESS_START_END_POSITIONS
                ),
                mock.call(
                    epaper.COMMANDS.SET_RAM_Y_ADDRESS_START_END_POSITIONS
                ),
                mock.call(epaper.COMMANDS.SET_RAM_X_ADDRESS_COUNTER),
                mock.call(epaper.COMMANDS.SET_RAM_Y_ADDRESS_COUNTER),
            ],
            any_order=True,
        )
        assert mock_epaper_driver_spi._send_byte.call_count == 13

    def test_set_does_not_work_when_display_is_off_unittest(
        self, mock_epaper_driver_spi: pytest_mock.MockType
    ) -> None:
        """Does not set display window when the display is off."""
        mock_epaper_driver_spi._is_screen_on = False

        mock_epaper_driver_spi._set_display_window(x=10, y=20, w=50, h=30)

        mock_epaper_driver_spi._send_command.assert_not_called()
        mock_epaper_driver_spi._send_byte.assert_not_called()

    @pytest.mark.parametrize(
        "x,y,w,h",
        [(-1, 1, 5, 5), (1, -1, 5, 5), (1, 1, -1, 5), (1, 1, 5, -1)],
    )
    def test_set_does_not_work_when_any_arg_is_negative_unittest(
        self,
        mock_epaper_driver_spi: pytest_mock.MockType,
        x: int,
        y: int,
        w: int,
        h: int,
    ) -> None:
        """Does not set display window when any argument is negative."""
        mock_epaper_driver_spi._is_screen_on = True
        mock_epaper_driver_spi._width = 100
        mock_epaper_driver_spi._height = 100

        mock_epaper_driver_spi._set_display_window(x=x, y=y, w=w, h=h)

        mock_epaper_driver_spi._send_command.assert_not_called()
        mock_epaper_driver_spi._send_byte.assert_not_called()


class TestEPaperDriverWriteBufferToBwRam:
    """Test EPaperDriver _write_buffer_to_bw_ram."""

    def test_write_works_when_display_is_on_unittest(
        self, mock_epaper_driver_spi: pytest_mock.MockType
    ) -> None:
        """Write BW RAM works when the display is on."""
        mock_epaper_driver_spi._is_screen_on = True

        mock_epaper_driver_spi._write_buffer_to_bw_ram(bytearray(0x03))

        mock_epaper_driver_spi._send_command.assert_called_once_with(
            epaper.COMMANDS.WRITE_BW_RAM
        )
        mock_epaper_driver_spi._send_block.assert_called_once_with(
            bytearray(0x03)
        )

    def test_write_does_not_work_when_display_is_off_unittest(
        self, mock_epaper_driver_spi: pytest_mock.MockType
    ) -> None:
        """Does not write BW RAM when the display is off."""
        mock_epaper_driver_spi._is_screen_on = False

        mock_epaper_driver_spi._write_buffer_to_bw_ram(bytearray(0x03))

        mock_epaper_driver_spi._send_command.assert_not_called()
        mock_epaper_driver_spi._send_block.assert_not_called()


class TestEPaperDriverWriteBufferToRedRam:
    """Test EPaperDriver _write_buffer_to_bw_ram."""

    def test_write_works_when_display_is_on_unittest(
        self, mock_epaper_driver_spi: pytest_mock.MockType
    ) -> None:
        """Write Red RAM when the display is on."""
        mock_epaper_driver_spi._is_screen_on = True

        mock_epaper_driver_spi._write_buffer_to_red_ram(bytearray(0x04))

        mock_epaper_driver_spi._send_command.assert_called_once_with(
            epaper.COMMANDS.WRITE_RED_RAM
        )
        mock_epaper_driver_spi._send_block.assert_called_once_with(
            bytearray(0x04)
        )

    def test_write_does_not_work_when_display_is_off_unittest(
        self, mock_epaper_driver_spi: pytest_mock.MockType
    ) -> None:
        """Does not write Red RAM when the display is off."""
        mock_epaper_driver_spi._is_screen_on = False

        mock_epaper_driver_spi._write_buffer_to_red_ram(bytearray(0x04))

        mock_epaper_driver_spi._send_command.assert_not_called()
        mock_epaper_driver_spi._send_block.assert_not_called()


class TestEPaperDriverGetPartialFrames:
    """Test EPaperDriver _get_partial_frames."""

    def test_get_regular_bounded_frames_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Get frames that are within the bounds of the display."""
        current_frame = bytearray(
            0xFF if i % 3 == 0 else 0x00 for i in range(100 * 100)
        )
        previous_frame = bytearray(
            0x00 if i % 3 == 0 else 0xFF for i in range(100 * 100)
        )
        display = epaper.EPaperDriver(mocker.Mock())
        display._width = 200
        display._height = 100
        display._width_bytes = display._width // 8
        display._current_frame = current_frame
        display._previous_frame = previous_frame

        x, y, w, h = 9, 10, 15, 3
        partial_curr_frame, partial_prev_frame = display._get_partial_frames(
            x=x, y=y, w=w, h=h
        )

        # x_byte is x rounded up to the nearest multiple of 8
        # and w_byte is w rounded up to the nearest multiple of 8
        x_byte, w_byte = 8, 16

        assert len(partial_curr_frame) == (w_byte // 8) * h
        assert len(partial_prev_frame) == (w_byte // 8) * h

        expected_curr = bytearray()
        expected_prev = bytearray()

        # current frame row 0
        dst_start = 0 * (w_byte // 8)
        src_start = (0 + y) * (200 // 8) + (x_byte // 8)
        expected_curr[dst_start : dst_start + (w_byte // 8)] = current_frame[
            src_start : src_start + (w_byte // 8)
        ]
        assert (
            partial_curr_frame[dst_start : dst_start + (w_byte // 8)]
            == expected_curr[dst_start : dst_start + (w_byte // 8)]
        )

        # current frame row 1
        dst_start = 1 * (w_byte // 8)
        src_start = (1 + y) * (200 // 8) + (x_byte // 8)
        expected_curr[dst_start : dst_start + (w_byte // 8)] = current_frame[
            src_start : src_start + (w_byte // 8)
        ]
        assert (
            partial_curr_frame[dst_start : dst_start + (w_byte // 8)]
            == expected_curr[dst_start : dst_start + (w_byte // 8)]
        )

        # current frame row 2
        dst_start = 2 * (w_byte // 8)
        src_start = (2 + y) * (200 // 8) + (x_byte // 8)
        expected_curr[dst_start : dst_start + (w_byte // 8)] = current_frame[
            src_start : src_start + (w_byte // 8)
        ]
        assert (
            partial_curr_frame[dst_start : dst_start + (w_byte // 8)]
            == expected_curr[dst_start : dst_start + (w_byte // 8)]
        )

        # previous frame row 0
        dst_start = 0 * (w_byte // 8)
        src_start = (0 + y) * (200 // 8) + (x_byte // 8)
        expected_prev[dst_start : dst_start + (w_byte // 8)] = previous_frame[
            src_start : src_start + (w_byte // 8)
        ]
        assert (
            partial_prev_frame[dst_start : dst_start + (w_byte // 8)]
            == expected_prev[dst_start : dst_start + (w_byte // 8)]
        )

        # previous frame row 1
        dst_start = 1 * (w_byte // 8)
        src_start = (1 + y) * (200 // 8) + (x_byte // 8)
        expected_prev[dst_start : dst_start + (w_byte // 8)] = previous_frame[
            src_start : src_start + (w_byte // 8)
        ]
        assert (
            partial_prev_frame[dst_start : dst_start + (w_byte // 8)]
            == expected_prev[dst_start : dst_start + (w_byte // 8)]
        )

        # previous frame row 2
        dst_start = 2 * (w_byte // 8)
        src_start = (2 + y) * (200 // 8) + (x_byte // 8)
        expected_prev[dst_start : dst_start + (w_byte // 8)] = previous_frame[
            src_start : src_start + (w_byte // 8)
        ]
        assert (
            partial_prev_frame[dst_start : dst_start + (w_byte // 8)]
            == expected_prev[dst_start : dst_start + (w_byte // 8)]
        )

    def test_get_bounded_frames_limited_by_width_and_height_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Get frames that attempted to go beyond the bounds of the display."""
        current_frame = bytearray(
            0xFF if i % 3 == 0 else 0x00 for i in range(32 * 3)
        )
        previous_frame = bytearray(
            0x00 if i % 3 == 0 else 0xFF for i in range(32 * 3)
        )
        display = epaper.EPaperDriver(mocker.Mock())
        display._width = 32
        display._height = 3
        display._width_bytes = display._width // 8
        display._current_frame = current_frame
        display._previous_frame = previous_frame

        x, y, w, h = 9, 1, 31, 3
        partial_curr_frame, partial_prev_frame = display._get_partial_frames(
            x=x, y=y, w=w, h=h
        )

        w = display._width - x  # limited by width; expected: 23
        h = display._height - y  # limited by height; expected: 2

        # x_byte is x rounded up to the nearest multiple of 8
        # and w_byte is w rounded up to the nearest multiple of 8
        x_byte, w_byte = 8, 24

        assert len(partial_curr_frame) == (w_byte // 8) * h
        assert len(partial_prev_frame) == (w_byte // 8) * h

        expected_curr = bytearray()
        expected_prev = bytearray()

        # current frame row 0
        dst_start = 0 * (w_byte // 8)
        src_start = (0 + y) * (200 // 8) + (x_byte // 8)
        expected_curr[dst_start : dst_start + (w_byte // 8)] = current_frame[
            src_start : src_start + (w_byte // 8)
        ]
        assert (
            partial_curr_frame[dst_start : dst_start + (w_byte // 8)]
            == expected_curr[dst_start : dst_start + (w_byte // 8)]
        )

        # current frame row 1
        dst_start = 1 * (w_byte // 8)
        src_start = (1 + y) * (200 // 8) + (x_byte // 8)
        expected_curr[dst_start : dst_start + (w_byte // 8)] = current_frame[
            src_start : src_start + (w_byte // 8)
        ]
        assert (
            partial_curr_frame[dst_start : dst_start + (w_byte // 8)]
            == expected_curr[dst_start : dst_start + (w_byte // 8)]
        )

        # previous frame row 0
        dst_start = 0 * (w_byte // 8)
        src_start = (0 + y) * (200 // 8) + (x_byte // 8)
        expected_prev[dst_start : dst_start + (w_byte // 8)] = previous_frame[
            src_start : src_start + (w_byte // 8)
        ]
        assert (
            partial_prev_frame[dst_start : dst_start + (w_byte // 8)]
            == expected_prev[dst_start : dst_start + (w_byte // 8)]
        )

        # previous frame row 1
        dst_start = 1 * (w_byte // 8)
        src_start = (1 + y) * (200 // 8) + (x_byte // 8)
        expected_prev[dst_start : dst_start + (w_byte // 8)] = previous_frame[
            src_start : src_start + (w_byte // 8)
        ]
        assert (
            partial_prev_frame[dst_start : dst_start + (w_byte // 8)]
            == expected_prev[dst_start : dst_start + (w_byte // 8)]
        )

    @pytest.mark.parametrize(
        "x,y,w,h",
        [(-1, 1, 5, 5), (1, -1, 5, 5), (1, 1, -1, 5), (1, 1, 5, -1)],
    )
    def test_get_does_not_work_when_any_arg_is_negative_unittest(
        self, mocker: pytest_mock.MockerFixture, x: int, y: int, w: int, h: int
    ) -> None:
        """Returns empty bytearrays when any argument is negative."""
        current_frame = bytearray(
            0xFF if i % 3 == 0 else 0x00 for i in range(10 * 10)
        )
        previous_frame = bytearray(
            0x00 if i % 3 == 0 else 0xFF for i in range(10 * 10)
        )
        display = epaper.EPaperDriver(mocker.Mock())
        display._width = 10
        display._height = 10
        display._width_bytes = display._width // 8
        display._current_frame = current_frame
        display._previous_frame = previous_frame

        partial_curr_frame, partial_prev_frame = display._get_partial_frames(
            x=x, y=y, w=w, h=h
        )

        assert len(partial_curr_frame) == 0
        assert len(partial_prev_frame) == 0


class TestEPaperDriverSwapFrames:
    """Test EPaperDriver _swap_frames."""

    def test_swap_current_and_previous_frames_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Swap current and previous frames."""
        current_frame = bytearray()
        previous_frame = bytearray()
        display = epaper.EPaperDriver(mocker.Mock())
        display._current_frame = current_frame
        display._previous_frame = previous_frame

        display._swap_frames()

        assert display._current_frame is previous_frame
        assert display._previous_frame is current_frame


class TestEPaperDriverWakeDisplay:
    """Test EPaperDriver wake_display."""

    def test_wake_works_properly_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Wake display works properly."""
        mock_enable = mocker.patch.object(
            mock_epaper_driver_spi, "_enable_hardware", return_value=None
        )
        mock_reset = mocker.patch.object(
            mock_epaper_driver_spi, "_reset_display", return_value=None
        )
        mock_clear = mocker.patch.object(
            mock_epaper_driver_spi, "clear_frame_buffers", return_value=None
        )

        mock_epaper_driver_spi.wake_display()

        mock_enable.assert_called_once()
        mock_reset.assert_called_once()
        mock_clear.assert_called_once()
        mock_epaper_driver_spi._wait_on_busy.assert_called_once()
        mock_epaper_driver_spi._send_command.assert_has_calls(
            [
                mock.call(epaper.COMMANDS.SW_RESET),
                mock.call(epaper.COMMANDS.TEMPERATURE_SENSOR_CONTROL),
                mock.call(epaper.COMMANDS.BOOSTER_SOFT_START_CONTROL),
                mock.call(epaper.COMMANDS.DRIVER_OUTPUT_CONTROL),
                mock.call(epaper.COMMANDS.BORDER_WAVEFORM_CONTROL),
            ],
            any_order=True,
        )
        assert mock_epaper_driver_spi._send_byte.call_count == 10


class TestEPaperDriverRefreshDisplay:
    """Test EPaperDrvier refresh_display."""

    def test_refresh_does_not_work_when_display_is_off_unittest(
        self, mock_epaper_driver_spi: pytest_mock.MockType
    ) -> None:
        """Does not refresh display when the display is off."""
        mock_epaper_driver_spi._is_screen_on = False

        mock_epaper_driver_spi.refresh_display(epaper.REFRESHMODES.FULL)

        mock_epaper_driver_spi._send_command.assert_not_called()
        mock_epaper_driver_spi._send_byte.assert_not_called()
        mock_epaper_driver_spi._wait_on_busy.assert_not_called()

    def test_refresh_powers_on_display_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Power on display."""
        mock_epaper_driver_spi._is_screen_on = True
        mock_spi_calls = mocker.Mock()
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._send_command, "_send_command"
        )
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._send_byte, "_send_byte"
        )
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._wait_on_busy, "_wait_on_busy"
        )

        mock_epaper_driver_spi.refresh_display(
            mode=mocker.Mock(), power_on_display=True
        )

        mock_spi_calls.assert_has_calls(
            [
                mock.call._send_command(
                    epaper.COMMANDS.DISPLAY_UPDATE_CONTROL_1
                ),
                mock.call._send_byte(0x00),  # default
                mock.call._send_command(
                    epaper.COMMANDS.DISPLAY_UPDATE_CONTROL_2
                ),
                mock.call._send_byte(0xC0),  # powers on display
                mock.call._send_command(epaper.COMMANDS.MASTER_ACTIVATION),
                mock.call._wait_on_busy(),
            ]
        )

    def test_refresh_powers_off_display_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Power off display."""
        mock_epaper_driver_spi._is_screen_on = True
        mock_spi_calls = mocker.Mock()
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._send_command, "_send_command"
        )
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._send_byte, "_send_byte"
        )
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._wait_on_busy, "_wait_on_busy"
        )

        mock_epaper_driver_spi.refresh_display(
            mode=mocker.Mock(), power_off_display=True
        )

        mock_spi_calls.assert_has_calls(
            [
                mock.call._send_command(
                    epaper.COMMANDS.DISPLAY_UPDATE_CONTROL_1
                ),
                mock.call._send_byte(0x00),  # default
                mock.call._send_command(
                    epaper.COMMANDS.DISPLAY_UPDATE_CONTROL_2
                ),
                mock.call._send_byte(0x03),  # powers off display
                mock.call._send_command(epaper.COMMANDS.MASTER_ACTIVATION),
                mock.call._wait_on_busy(),
            ]
        )

    def test_refresh_display_on_full_mode_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Refresh display on full mode."""
        mock_epaper_driver_spi._is_screen_on = True
        mock_spi_calls = mocker.Mock()
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._send_command, "_send_command"
        )
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._send_byte, "_send_byte"
        )
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._wait_on_busy, "_wait_on_busy"
        )

        mock_epaper_driver_spi.refresh_display(mode=epaper.REFRESHMODES.FULL)

        mock_spi_calls.assert_has_calls(
            [
                mock.call._send_command(
                    epaper.COMMANDS.DISPLAY_UPDATE_CONTROL_1
                ),
                mock.call._send_byte(0x40),  # no buffer comparison
                mock.call._send_command(
                    epaper.COMMANDS.DISPLAY_UPDATE_CONTROL_2
                ),
                mock.call._send_byte(0x34),  # full refresh
                mock.call._send_command(epaper.COMMANDS.MASTER_ACTIVATION),
                mock.call._wait_on_busy(),
            ]
        )

    def test_refresh_display_on_fast_mode_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Refresh display on fast mode."""
        mock_epaper_driver_spi._is_screen_on = True
        mock_spi_calls = mocker.Mock()
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._send_command, "_send_command"
        )
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._send_byte, "_send_byte"
        )
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._wait_on_busy, "_wait_on_busy"
        )

        mock_epaper_driver_spi.refresh_display(mode=epaper.REFRESHMODES.FAST)

        mock_spi_calls.assert_has_calls(
            [
                mock.call._send_command(
                    epaper.COMMANDS.WRITE_TO_TEMPERATURE_REGISTER
                ),
                mock.call._send_byte(0x6A),  # temperature for fast refresh
                mock.call._send_command(
                    epaper.COMMANDS.DISPLAY_UPDATE_CONTROL_1
                ),
                mock.call._send_byte(0x40),  # no buffer comparison
                mock.call._send_command(
                    epaper.COMMANDS.DISPLAY_UPDATE_CONTROL_2
                ),
                mock.call._send_byte(0x04),  # fast refresh
                mock.call._send_command(epaper.COMMANDS.MASTER_ACTIVATION),
                mock.call._wait_on_busy(),
            ]
        )

    def test_refresh_display_on_partial_mode_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Refresh display on partial mode."""
        mock_epaper_driver_spi._is_screen_on = True
        mock_spi_calls = mocker.Mock()
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._send_command, "_send_command"
        )
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._send_byte, "_send_byte"
        )
        mock_spi_calls.attach_mock(
            mock_epaper_driver_spi._wait_on_busy, "_wait_on_busy"
        )

        mock_epaper_driver_spi.refresh_display(
            mode=epaper.REFRESHMODES.PARTIAL
        )

        mock_spi_calls.assert_has_calls(
            [
                mock.call._send_command(
                    epaper.COMMANDS.DISPLAY_UPDATE_CONTROL_1
                ),
                mock.call._send_byte(0x00),  # buffer comparison
                mock.call._send_command(
                    epaper.COMMANDS.DISPLAY_UPDATE_CONTROL_2
                ),
                mock.call._send_byte(0x1C),  # full refresh
                mock.call._send_command(epaper.COMMANDS.MASTER_ACTIVATION),
                mock.call._wait_on_busy(),
            ]
        )


class TestEPaperDriverDeepSleep:
    """Test EPaperDriver deep_sleep."""

    def test_sleep_works_when_display_is_on_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Deep sleep when the display is on."""
        mock_sleep = mocker.patch("time.sleep")
        mock_close_hw = mocker.patch.object(
            mock_epaper_driver_spi, "_close_hardware", return_value=None
        )
        mock_epaper_driver_spi._is_screen_on = True

        mock_epaper_driver_spi.deep_sleep()

        mock_epaper_driver_spi._send_command.assert_has_calls(
            [
                mock.call(epaper.COMMANDS.DISPLAY_UPDATE_CONTROL_2),
                mock.call(epaper.COMMANDS.MASTER_ACTIVATION),
                mock.call(epaper.COMMANDS.DEEP_SLEEP_MODE),
            ]
        )
        assert mock_epaper_driver_spi._send_byte.call_count == 2
        mock_sleep.assert_called_once_with(0.01)
        mock_close_hw.assert_called_once()

    def test_sleep_does_not_work_when_display_is_off_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Does not deep sleep when display is off."""
        mock_sleep = mocker.patch("time.sleep")
        mock_close_hw = mocker.patch.object(
            mock_epaper_driver_spi, "_close_hardware", return_value=None
        )
        mock_epaper_driver_spi._is_screen_on = False

        mock_epaper_driver_spi.deep_sleep()

        mock_epaper_driver_spi._send_command.assert_not_called()
        mock_epaper_driver_spi._send_byte.assert_not_called()
        mock_sleep.assert_not_called()
        mock_close_hw.assert_not_called()


class TestEPaperDriverWriteFrameBuffers:
    """Test EPaperDriver write_frame_buffers."""

    def test_write_works_when_display_is_on_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Write frame buffers when the display is on."""
        mock_set_disp_window = mocker.patch.object(
            mock_epaper_driver_spi, "_set_display_window", return_value=None
        )
        mock_write_bw = mocker.patch.object(
            mock_epaper_driver_spi,
            "_write_buffer_to_bw_ram",
            return_value=None,
        )
        mock_write_red = mocker.patch.object(
            mock_epaper_driver_spi,
            "_write_buffer_to_red_ram",
            return_value=None,
        )
        mock_epaper_driver_spi._is_screen_on = True
        mock_epaper_driver_spi._width = 100
        mock_epaper_driver_spi._height = 150
        current_frame = bytearray()
        mock_epaper_driver_spi._current_frame = current_frame

        mock_epaper_driver_spi.write_frame_buffers()

        mock_set_disp_window.assert_called_once_with(
            x=0,
            y=0,
            w=mock_epaper_driver_spi._width,
            h=mock_epaper_driver_spi._height,
        )
        mock_write_bw.assert_called_once_with(current_frame)
        mock_write_red.assert_called_once_with(current_frame)

    def test_write_does_not_work_when_display_is_off_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Does not write frame buffers when the display is off."""
        mock_set_disp_window = mocker.patch.object(
            mock_epaper_driver_spi, "_set_display_window", return_value=None
        )
        mock_write_bw = mocker.patch.object(
            mock_epaper_driver_spi,
            "_write_buffer_to_bw_ram",
            return_value=None,
        )
        mock_write_red = mocker.patch.object(
            mock_epaper_driver_spi,
            "_write_buffer_to_red_ram",
            return_value=None,
        )
        mock_epaper_driver_spi._is_screen_on = False
        mock_epaper_driver_spi._width = 100
        mock_epaper_driver_spi._height = 150
        current_frame = bytearray()
        mock_epaper_driver_spi._current_frame = current_frame

        mock_epaper_driver_spi.write_frame_buffers()

        mock_set_disp_window.assert_not_called()
        mock_write_bw.assert_not_called()
        mock_write_red.assert_not_called()


class TestEPaperDriverWritePartialFrameBuffers:
    """Test EPaperDriver write_partial_frame_buffers."""

    def test_write_works_when_display_is_on_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Write partial frame buffers when the display is on."""
        partial_curr_frame = bytearray()
        partial_prev_frame = bytearray()
        mock_get_part_frames = mocker.patch.object(
            mock_epaper_driver_spi,
            "_get_partial_frames",
            return_value=(partial_curr_frame, partial_prev_frame),
        )
        mock_set_disp_window = mocker.patch.object(
            mock_epaper_driver_spi, "_set_display_window", return_value=None
        )
        mock_write_bw = mocker.patch.object(
            mock_epaper_driver_spi,
            "_write_buffer_to_bw_ram",
            return_value=None,
        )
        mock_write_red = mocker.patch.object(
            mock_epaper_driver_spi,
            "_write_buffer_to_red_ram",
            return_value=None,
        )
        mock_swap_frames = mocker.patch.object(
            mock_epaper_driver_spi,
            "_swap_frames",
            return_value=None,
        )
        mock_epaper_driver_spi._is_screen_on = True

        mock_epaper_driver_spi.write_partial_frame_buffers(
            x=5, y=10, w=20, h=25
        )

        mock_get_part_frames.assert_called_once_with(x=5, y=10, w=20, h=25)
        mock_set_disp_window.assert_called_once_with(x=5, y=10, w=20, h=25)
        mock_write_bw.assert_called_once_with(partial_curr_frame)
        mock_write_red.assert_called_once_with(partial_curr_frame)
        mock_swap_frames.assert_called_once()

    def test_write_does_not_work_when_display_is_off_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Does not write partial frame buffers when the display is off."""
        partial_curr_frame = bytearray()
        partial_prev_frame = bytearray()
        mock_get_part_frames = mocker.patch.object(
            mock_epaper_driver_spi,
            "_get_partial_frames",
            return_value=(partial_curr_frame, partial_prev_frame),
        )
        mock_set_disp_window = mocker.patch.object(
            mock_epaper_driver_spi, "_set_display_window", return_value=None
        )
        mock_write_bw = mocker.patch.object(
            mock_epaper_driver_spi,
            "_write_buffer_to_bw_ram",
            return_value=None,
        )
        mock_write_red = mocker.patch.object(
            mock_epaper_driver_spi,
            "_write_buffer_to_red_ram",
            return_value=None,
        )
        mock_swap_frames = mocker.patch.object(
            mock_epaper_driver_spi,
            "_swap_frames",
            return_value=None,
        )
        mock_epaper_driver_spi._is_screen_on = False

        mock_epaper_driver_spi.write_partial_frame_buffers(
            x=5, y=10, w=20, h=25
        )

        mock_get_part_frames.assert_not_called()
        mock_set_disp_window.assert_not_called()
        mock_write_bw.assert_not_called()
        mock_write_red.assert_not_called()
        mock_swap_frames.assert_not_called()


class TestEPaperDriverClearFrameBuffers:
    """Test EPaperDriver clear_frame_buffers."""

    def test_clear_works_when_display_is_on_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Clear frame buffers when the display is on."""
        mock_set_disp_window = mocker.patch.object(
            mock_epaper_driver_spi, "_set_display_window", return_value=None
        )
        mock_epaper_driver_spi._is_screen_on = True
        mock_epaper_driver_spi._width = 100
        mock_epaper_driver_spi._height = 150
        mock_epaper_driver_spi._buffer_size = 10
        mock_epaper_driver_spi._current_frame = bytearray()
        mock_epaper_driver_spi._previous_frame = bytearray()

        mock_epaper_driver_spi.clear_frame_buffers()

        assert len(mock_epaper_driver_spi._current_frame) == 10
        assert len(mock_epaper_driver_spi._previous_frame) == 10
        mock_set_disp_window.assert_called_once_with(
            x=0,
            y=0,
            w=mock_epaper_driver_spi._width,
            h=mock_epaper_driver_spi._height,
        )
        mock_epaper_driver_spi._send_command.assert_has_calls(
            [
                mock.call(epaper.COMMANDS.AUTO_WRITE_BW_RAM),
                mock.call(epaper.COMMANDS.AUTO_WRITE_RED_RAM),
            ]
        )
        assert mock_epaper_driver_spi._send_byte.call_count == 2
        assert mock_epaper_driver_spi._wait_on_busy.call_count == 2

    def test_clear_does_not_work_when_display_is_off_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_epaper_driver_spi: pytest_mock.MockType,
    ) -> None:
        """Does not clear frame buffers when the display is off."""
        current_frame = bytearray()
        previous_frame = bytearray()
        mock_set_disp_window = mocker.patch.object(
            mock_epaper_driver_spi, "_set_display_window", return_value=None
        )
        mock_epaper_driver_spi._is_screen_on = False
        mock_epaper_driver_spi._width = 100
        mock_epaper_driver_spi._height = 150
        mock_epaper_driver_spi._buffer_size = 10
        mock_epaper_driver_spi._current_frame = current_frame
        mock_epaper_driver_spi._previous_frame = previous_frame

        mock_epaper_driver_spi.clear_frame_buffers()

        assert mock_epaper_driver_spi._current_frame is current_frame
        assert mock_epaper_driver_spi._previous_frame is previous_frame
        mock_set_disp_window.assert_not_called()
        mock_epaper_driver_spi._send_command.assert_not_called()
        mock_epaper_driver_spi._send_byte.assert_not_called()
        mock_epaper_driver_spi._wait_on_busy.assert_not_called()


class TestEPaperDriverDrawFrame:
    """Test EPaperDriver draw_frame."""

    def test_draw_full_screen_image_unittest(
        self, mock_epaper_driver: epaper.EPaperDriver
    ) -> None:
        """Draw an image that covers the entire screen."""
        mock_epaper_driver._width = 80
        mock_epaper_driver._height = 160
        mock_epaper_driver._width_bytes = mock_epaper_driver._width // 8
        mock_epaper_driver._current_frame = bytearray(
            mock_epaper_driver._width_bytes * mock_epaper_driver._height
        )

        image = Image.new(
            "1",
            (mock_epaper_driver._width, mock_epaper_driver._height),
            epaper.COLORS.BLACK,
        )
        mock_epaper_driver.draw_frame(image)

        assert (
            len(mock_epaper_driver._current_frame)
            == (image.width // 8) * image.height
        )
        assert 0xFF not in mock_epaper_driver._current_frame

    def test_draw_full_screen_image_offset_unittest(
        self, mock_epaper_driver: epaper.EPaperDriver
    ) -> None:
        """Draw an image that covers entire screen but offset by x and y.

        Limits write due to the image going off-screen.
        """
        width = 80
        width_bytes = width // 8
        height = 160
        mock_epaper_driver._width = width
        mock_epaper_driver._height = height
        mock_epaper_driver._width_bytes = width_bytes
        mock_epaper_driver._current_frame = bytearray(
            0xFF for _ in range(width_bytes * height)
        )

        image = Image.new("1", (width, height), 0x00)
        mock_epaper_driver.draw_frame(image, x=8, y=1)

        current_frame = mock_epaper_driver._current_frame

        assert len(current_frame) == (image.width // 8) * image.height
        assert 0x00 in current_frame
        assert 0xFF in current_frame

        # First row is all 0xFF due to image y offset
        assert 0x00 not in current_frame[0 : width_bytes + 1]

        # First column is all 0xFF due to image x offset (in bytes)
        rows = bytearray()
        for row in range(height):
            start = row * width_bytes
            rows.extend(current_frame[start : start + 1])
        assert 0x00 not in rows


class TestEPaperDriverFillFrame:
    """Test EPaperDriver fill_frame."""

    def test_fill_entire_screen_with_color_unittest(
        self, mock_epaper_driver: epaper.EPaperDriver
    ) -> None:
        """Fill entire screen with the color black."""
        width = 80
        width_bytes = width // 8
        height = 80
        mock_epaper_driver._buffer_size = width_bytes * height
        mock_epaper_driver._current_frame = bytearray(
            0xFF for _ in range(width_bytes * height)
        )

        mock_epaper_driver.fill_frame(epaper.COLORS.BLACK)

        current_frame = mock_epaper_driver._current_frame

        assert len(current_frame) == (width_bytes) * height
        assert 0xFF not in current_frame
