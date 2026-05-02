import enum
import time

from PIL import Image

from pireaderos.hal import manager


class PINS:
    """The pins to drive the e-paper display."""

    RESET = 17
    BUSY = 24
    DC = 25


class DIMENSIONS:
    """The screen dimensions of the e-paper display."""

    WIDTH = 800
    HEIGHT = 480
    WIDTH_BYTES = WIDTH // 8
    BUFFER_SIZE = WIDTH_BYTES * HEIGHT


class COMMANDS(enum.IntEnum):
    """The commands to drive the e-paper display."""

    SW_RESET = 0x12
    TEMPERATURE_SENSOR_CONTROL = 0x18
    WRITE_TO_TEMPERATURE_REGISTER = 0x1A
    BOOSTER_SOFT_START_CONTROL = 0x0C
    DRIVER_OUTPUT_CONTROL = 0x01
    BORDER_WAVEFORM_CONTROL = 0x3C
    AUTO_WRITE_BW_RAM = 0x47
    AUTO_WRITE_RED_RAM = 0x46
    WRITE_BW_RAM = 0x24
    WRITE_RED_RAM = 0x26
    DATA_ENTRY_MODE_SETTING = 0x11
    SET_RAM_X_ADDRESS_START_END_POSITIONS = 0x44
    SET_RAM_Y_ADDRESS_START_END_POSITIONS = 0x45
    SET_RAM_X_ADDRESS_COUNTER = 0x4E
    SET_RAM_Y_ADDRESS_COUNTER = 0x4F
    DISPLAY_UPDATE_CONTROL_1 = 0x21
    DISPLAY_UPDATE_CONTROL_2 = 0x22
    MASTER_ACTIVATION = 0x20
    DEEP_SLEEP_MODE = 0x10


class REFRESHMODES(enum.StrEnum):
    """The modes to refresh the e-paper display."""

    FULL = enum.auto()
    FAST = enum.auto()
    PARTIAL = enum.auto()


class COLORS(enum.IntEnum):
    """The supported colors on the e-paper display."""

    BLACK = 0x00
    WHITE = 0xFF


class EPaperDriver:
    """Driver for the Good Display 4.26 inch e-paper display.

    Model: GDEQ0426T82-FT01C.
    Adapter board: ESP32-FTS02.
    Platform: Raspberry Pi Zero 2W.

    Examples:
      Full lifecycle of e-paper display, from initialization to deep sleep::

        display = EPaperDriver(hardware_manager)
        display.wake_display()
        display.draw_frame(image) # draw image to buffers
        display.write_frame_buffers() # write buffers to display's RAM
        display.refresh_display(
            REFRESHMODES.FULL,
            power_on_display=True,
            power_off_display=True,
        )
        display.deep_sleep()

      Clear e-paper display::

        display.clear_frame_buffers() # clear buffers and display's RAM
        display.refresh_display(REFRESHMODES.FULL)

    """

    def __init__(self, hw: manager.HardwareManager) -> None:
        self._hw = hw
        self._is_screen_on = False

        self._width = DIMENSIONS.WIDTH
        self._height = DIMENSIONS.HEIGHT
        self._width_bytes = DIMENSIONS.WIDTH_BYTES
        self._buffer_size = DIMENSIONS.BUFFER_SIZE

        # Previous and current frame buffers
        self._previous_frame = bytearray(
            0xFF for _ in range(self._buffer_size)
        )
        self._current_frame = bytearray(0xFF for _ in range(self._buffer_size))

    def _enable_hardware(self) -> None:
        """Enable hardware resources for the e-paper display."""
        if self._is_screen_on:
            return

        self._hw.enable_spi()
        self._reset_pin = self._hw.request_pin(PINS.RESET, "output")
        self._dc_pin = self._hw.request_pin(PINS.DC, "output")
        self._busy_pin = self._hw.request_pin(PINS.BUSY, "input")

        self._is_screen_on = True

    def _close_hardware(self) -> None:
        """Release hardware resources for the e-paper display."""
        if not self._is_screen_on:
            return

        self._hw.close_spi()
        self._hw.release_pin(self._reset_pin)
        self._hw.release_pin(self._dc_pin)
        self._hw.release_pin(self._busy_pin)

        self._is_screen_on = False

    def _reset_display(self) -> None:
        """Reset the e-paper display using the reset GPIO."""
        if not self._is_screen_on:
            return

        self._reset_pin.on()
        time.sleep(0.02)  # 20 ms
        self._reset_pin.off()
        time.sleep(0.002)  # 2 ms
        self._reset_pin.on()
        time.sleep(0.02)  # 20 ms

    def _wait_on_busy(self) -> None:
        """Wait until the display signals it is ready."""
        if not self._is_screen_on:
            return

        while self._busy_pin.is_active:
            time.sleep(0.02)  # 20 ms
        time.sleep(0.02)  # 20 ms

    def _send_command(self, command: COMMANDS) -> None:
        """Send a command byte over SPI."""
        if not self._is_screen_on:
            return

        self._dc_pin.off()
        self._hw.spi_writebytes([command])

    def _send_byte(self, byte: int) -> None:
        """Send a data byte over SPI."""
        if not self._is_screen_on:
            return

        self._dc_pin.on()
        self._hw.spi_writebytes([byte])

    def _send_block(self, data: bytearray) -> None:
        """Send multiple data bytes over SPI."""
        if not self._is_screen_on:
            return

        self._dc_pin.on()
        self._hw.spi_writebytes2(data)

    def _set_display_window(self, *, x: int, y: int, w: int, h: int) -> None:
        """Set the active RAM window for drawing."""
        if not self._is_screen_on:
            return

        if x + w >= self._width:  # limit width
            w = self._width - x

        if y + h >= self._height:  # limit height
            h = self._height - y

        if x < 0 or y < 0 or w < 0 or h < 0:
            return

        x -= x % 8  # byte boundary (rounded down to nearest multiple of 8)
        w += (8 - w) % 8  # byte boundary (rounded up to nearest multiple of 8)

        # Reverse y coordinate (gates on display are reversed)
        y = self._height - y - h

        # Set data entry mode (X+, Y-)
        self._send_command(COMMANDS.DATA_ENTRY_MODE_SETTING)
        self._send_byte(0x01)

        # Set RAM X address range (start, end) - X is in pixels
        self._send_command(COMMANDS.SET_RAM_X_ADDRESS_START_END_POSITIONS)
        self._send_byte(x % 256)  # start low byte
        self._send_byte(x // 256)  # start high byte
        self._send_byte((x + w - 1) % 256)  # end low byte
        self._send_byte((x + w - 1) // 256)  # end high byte

        # Set RAM Y address range (start, end) - Y is in pixels
        self._send_command(COMMANDS.SET_RAM_Y_ADDRESS_START_END_POSITIONS)
        self._send_byte((y + h - 1) % 256)  # start low byte
        self._send_byte((y + h - 1) // 256)  # start high byte
        self._send_byte(y % 256)  # end low byte
        self._send_byte(y // 256)  # end high byte

        # Set RAM X address counter - X is in pixels
        self._send_command(COMMANDS.SET_RAM_X_ADDRESS_COUNTER)
        self._send_byte(x % 256)  # low byte
        self._send_byte(x // 256)  # high byte

        # Set RAM Y address counter - Y is in pixels
        self._send_command(COMMANDS.SET_RAM_Y_ADDRESS_COUNTER)
        self._send_byte((y + h - 1) % 256)  # low byte
        self._send_byte((y + h - 1) // 256)  # high byte

    def _write_buffer_to_bw_ram(self, buffer: bytearray) -> None:
        """Write data to the black-and-white RAM."""
        if not self._is_screen_on:
            return

        self._send_command(COMMANDS.WRITE_BW_RAM)
        self._send_block(buffer)

    def _write_buffer_to_red_ram(self, buffer: bytearray) -> None:
        """Write data to the red RAM."""
        if not self._is_screen_on:
            return

        self._send_command(COMMANDS.WRITE_RED_RAM)
        self._send_block(buffer)

    def _get_partial_frames(
        self, *, x: int, y: int, w: int, h: int
    ) -> tuple[bytearray, bytearray]:
        """Return the current and previous frame data for a rectangle."""
        if x + w >= self._width:  # limit width
            w = self._width - x

        if y + h >= self._height:  # limit height
            h = self._height - y

        if x < 0 or y < 0 or w < 0 or h < 0:
            return bytearray(), bytearray()

        x -= x % 8  # byte boundary (rounded down to nearest multiple of 8)
        w += (8 - w) % 8  # byte boundary (rounded up to nearest multiple of 8)

        window_width_bytes = w // 8
        curr_frame = bytearray()
        prev_frame = bytearray()

        for row in range(h):
            src_y = y + row

            src_offset = src_y * self._width_bytes + (x // 8)
            dst_offset = row * window_width_bytes

            src_end = src_offset + window_width_bytes
            dst_end = dst_offset + window_width_bytes

            curr_frame[dst_offset:dst_end] = self._current_frame[
                src_offset:src_end
            ]
            prev_frame[dst_offset:dst_end] = self._previous_frame[
                src_offset:src_end
            ]

        return curr_frame, prev_frame

    def _swap_frames(self) -> None:
        """Swap current and previous frame buffers."""
        temp = self._previous_frame
        self._previous_frame = self._current_frame
        self._current_frame = temp

    def wake_display(self) -> None:
        """Initialize and power on the e-paper display."""
        self._enable_hardware()
        self._reset_display()

        # Software reset
        self._send_command(COMMANDS.SW_RESET)
        self._wait_on_busy()

        # Use internal temperature sensor
        self._send_command(COMMANDS.TEMPERATURE_SENSOR_CONTROL)
        self._send_byte(0x80)

        # Configure booster soft-start control
        self._send_command(COMMANDS.BOOSTER_SOFT_START_CONTROL)
        self._send_byte(0xAE)
        self._send_byte(0xC7)
        self._send_byte(0xC3)
        self._send_byte(0xC0)
        self._send_byte(0x40)

        # Configure gate settings
        self._send_command(COMMANDS.DRIVER_OUTPUT_CONTROL)
        self._send_byte((self._height - 1) % 256)  # gates A0...A7 (LSB)
        self._send_byte((self._height - 1) // 256)  # gates A8...A9 (MSB)
        self._send_byte(0x02)  # SM=1 (interlaced), TB=0

        # Configure border waveform
        self._send_command(COMMANDS.BORDER_WAVEFORM_CONTROL)
        self._send_byte(0x01)  # LUT1

        self.clear_frame_buffers()

    def refresh_display(
        self,
        mode: REFRESHMODES,
        *,
        power_on_display: bool = False,
        power_off_display: bool = False,
    ) -> None:
        """Refresh the display using the selected mode."""
        if not self._is_screen_on:
            return

        buffer_comparison = 0x00
        update_sequence = 0x00

        if power_on_display:
            update_sequence |= 0xC0  # CLOCK_ON, ANALOG_ON

        if power_off_display:
            update_sequence |= 0x03  # ANALOG_OFF, CLOCK_OFF

        if mode is REFRESHMODES.FULL:
            buffer_comparison |= 0x40  # Do not compare buffers
            update_sequence |= 0x34  # TEMP_LOAD, LUT_LOAD, DISPLAY_START
        elif mode is REFRESHMODES.FAST:
            # Write high temperature to the register for a faster refresh
            self._send_command(COMMANDS.WRITE_TO_TEMPERATURE_REGISTER)
            self._send_byte(0x6A)

            buffer_comparison |= 0x40  # Do not compare buffers
            update_sequence |= 0x04  # DISPLAY_START
        elif mode is REFRESHMODES.PARTIAL:
            buffer_comparison |= 0x00  # Compare buffers
            update_sequence |= 0x1C  # LUT_LOAD, MODE_SELECT 2, DISPLAY_START

        self._send_command(COMMANDS.DISPLAY_UPDATE_CONTROL_1)
        self._send_byte(buffer_comparison)

        self._send_command(COMMANDS.DISPLAY_UPDATE_CONTROL_2)
        self._send_byte(update_sequence)

        self._send_command(COMMANDS.MASTER_ACTIVATION)
        self._wait_on_busy()

    def deep_sleep(self) -> None:
        """Power off the display and enter deep sleep."""
        if not self._is_screen_on:
            return

        # Power off
        self._send_command(COMMANDS.DISPLAY_UPDATE_CONTROL_2)
        self._send_byte(0x83)

        self._send_command(COMMANDS.MASTER_ACTIVATION)
        self._wait_on_busy()

        # Enter deep sleep mode
        self._send_command(COMMANDS.DEEP_SLEEP_MODE)
        self._send_byte(0x03)

        time.sleep(0.01)  # 10 ms
        self._close_hardware()

    def write_frame_buffers(self) -> None:
        """Write the full current frame to display RAM."""
        if not self._is_screen_on:
            return

        self._set_display_window(x=0, y=0, w=self._width, h=self._height)

        # Write current frame to BW and Red RAM
        self._write_buffer_to_bw_ram(self._current_frame)
        self._write_buffer_to_red_ram(self._current_frame)

    def write_partial_frame_buffers(
        self, *, x: int, y: int, w: int, h: int
    ) -> None:
        """Write a partial update from current and previous buffers."""
        if not self._is_screen_on:
            return

        # Get bounded current and previous frames
        curr_frame, prev_frame = self._get_partial_frames(x=x, y=y, w=w, h=h)

        self._set_display_window(x=x, y=y, w=w, h=h)

        # Write bounded frames to RAM
        self._write_buffer_to_bw_ram(curr_frame)
        self._write_buffer_to_red_ram(prev_frame)

        self._swap_frames()

    def clear_frame_buffers(self) -> None:
        """Clear both frame buffers and the display RAM."""
        if not self._is_screen_on:
            return

        # Clear frames
        self._current_frame = bytearray(
            COLORS.WHITE for _ in range(self._buffer_size)
        )
        self._previous_frame = bytearray(
            COLORS.WHITE for _ in range(self._buffer_size)
        )

        self._set_display_window(x=0, y=0, w=self._width, h=self._height)

        # Fill entire BW RAM with white pattern
        self._send_command(COMMANDS.AUTO_WRITE_BW_RAM)
        self._send_byte(0xF7)
        self._wait_on_busy()

        # Fill entire Red RAM with white pattern
        self._send_command(COMMANDS.AUTO_WRITE_RED_RAM)
        self._send_byte(0xF7)
        self._wait_on_busy()

    def draw_frame(
        self, image: Image.Image, *, x: int = 0, y: int = 0
    ) -> None:
        """Render a PIL image into the current frame buffer."""
        image_width_bytes = image.width // 8
        pixels = image.tobytes()

        for row in range(image.height):
            dest_y = y + row
            if dest_y >= self._height:  # limit height
                break

            dest_offset = dest_y * self._width_bytes + (x // 8)
            src_offset = row * image_width_bytes

            for col in range(image_width_bytes):
                if x // 8 + col >= self._width_bytes:  # limit width
                    break

                self._current_frame[dest_offset + col] = pixels[
                    src_offset + col
                ]

    def fill_frame(self, color: COLORS) -> None:
        """Fill the current frame buffer with a single color."""
        self._current_frame = bytearray(
            color for _ in range(self._buffer_size)
        )
