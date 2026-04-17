import logging
import time
from collections.abc import Callable
from typing import Any

from pireaderos.hal import manager

logger = logging.getLogger(__name__)


I2C_ADDR = 0x38
INT_PIN = 19
RST_PIN = 26


# Touch data status
class _TD_STATUS:  # noqa: N801
    ADDR = 0x02

    # Masks
    TOUCH_POINTS = 0x0F


# Power consumption mode
class _ID_G_PMODE:  # noqa: N801
    ADDR = 0xA5

    # Write options
    ACTIVE = 0x00
    MONITOR = 0x01
    HIBERNATE = 0x03


class _TOUCH_LAYOUT:  # noqa: N801
    BASE_ADDR = 0x03
    STRIDE = 6  # bytes per touch point

    # Register offsets
    XH = 0x00
    XL = 0x01
    YH = 0x02
    YL = 0x03

    # Masks
    ID = 0xF0
    X_HIGH = 0x0F
    Y_HIGH = 0x0F


Touch = tuple[int, int, int]


def _touch_index(index: int, offset: int) -> int:
    """Get the register address for a given touch point index and offset."""
    return index * _TOUCH_LAYOUT.STRIDE + offset


class TouchDriver:
    """Driver for the FT6336U touch controller."""

    def __init__(
        self,
        hw: manager.HardwareManager,
        touch_int_callback: Callable[[list[Touch]], Any],
    ) -> None:
        """Initialize the touch controller hardware.

        Sets up GPIO pins for reset and interrupt, assigns the interrupt
        callback, and performs a hardware reset to ensure the FT6336U is in a
        known state.

        Args:
          hw:
            Hardware Abstraction Layer
          touch_int_callback:
            Callback function to handle touch interrupts.
            This function must accept a list of (int, int, int) tuples

        """
        self._hw = hw
        self._closed = False  # Flag for detecting clean up
        self._int_callback = touch_int_callback

        self._reset_pin = hw.request_pin(RST_PIN, mode="output")
        self._int_pin = hw.request_pin(
            INT_PIN,
            mode="input",
            pull_up=True,  # active-low
        )
        self._int_pin.set_when_activated(self._on_touch_interrupt)
        self.hardware_reset()

        logger.info("Initialized TouchDriver")

    def _on_touch_interrupt(self) -> None:
        """Call when a touch event is detected."""
        touches = self.read_touches()
        self._int_callback(touches)

    def hardware_reset(self) -> None:
        """Perform a hardware reset on the FT6336U touch controller.

        Sends a reset signal by setting the reset pin low for 10ms then high
        for 50ms, following the FT6336U datasheet timing requirements.
        """
        self._ensure_open()

        self._reset_pin.off()
        time.sleep(0.01)  # 10 ms
        self._reset_pin.on()
        time.sleep(0.05)  # 50 ms

    def set_power_mode(self, mode: str) -> None:
        """Change the power mode of the touch controller.

        Monitor mode scans at a reduced speed and power. When a touch
        is detected, the controller automatically enters active mode.

        Hibernate mode powers down the touch controller, so `hardware_reset`
        must be called to wake the device up and start receiving touch input.

        Args:
          mode:
            The mode to use. Must be one of 'active', 'monitor', or
            'hibernate'.

        """
        self._ensure_open()

        if mode == "active":
            self._hw.i2c_write(I2C_ADDR, _ID_G_PMODE.ADDR, _ID_G_PMODE.ACTIVE)
        elif mode == "monitor":
            self._hw.i2c_write(I2C_ADDR, _ID_G_PMODE.ADDR, _ID_G_PMODE.MONITOR)
        elif mode == "hibernate":
            self._hw.i2c_write(
                I2C_ADDR, _ID_G_PMODE.ADDR, _ID_G_PMODE.HIBERNATE
            )
        else:
            logger.error("Unknown mode: '%s'", mode)
            msg = f"Unknown mode: {mode}"
            raise ValueError(msg)
        time.sleep(0.05)  # 50 ms

    def _get_touch_count(self) -> int:
        """Return the number of touch points currently using."""
        status = self._hw.i2c_read_byte_data(I2C_ADDR, _TD_STATUS.ADDR)
        return status & _TD_STATUS.TOUCH_POINTS

    def read_touches(self) -> list[Touch]:
        """Return each touch point coordinate.

        Returns:
          A list of tuples containing (touch_id, x, y).

        """
        self._ensure_open()

        touch_points = self._get_touch_count()
        if touch_points == 0:
            return []

        length = touch_points * _TOUCH_LAYOUT.STRIDE
        data = self._hw.i2c_read_block_data(
            I2C_ADDR, _TOUCH_LAYOUT.BASE_ADDR, length
        )

        touches: list[Touch] = []

        for i in range(touch_points):
            xh = data[_touch_index(i, _TOUCH_LAYOUT.XH)]
            xl = data[_touch_index(i, _TOUCH_LAYOUT.XL)]
            yh = data[_touch_index(i, _TOUCH_LAYOUT.YH)]
            yl = data[_touch_index(i, _TOUCH_LAYOUT.YL)]

            touch_id = (yh & _TOUCH_LAYOUT.ID) >> 4
            x = ((xh & _TOUCH_LAYOUT.X_HIGH) << 8) | xl
            y = ((yh & _TOUCH_LAYOUT.Y_HIGH) << 8) | yl

            touches.append((touch_id, x, y))

        return touches

    def clean_up(self) -> None:
        """Clean up the touch controller's hardware resources."""
        if self._closed:
            return

        self._hw.release_pin(self._reset_pin)
        self._hw.release_pin(self._int_pin)

        self._closed = True

    def _ensure_open(self) -> None:
        if self._closed:
            logger.error("'TouchDriver' is closed")
            msg = "TouchDriver is closed"
            raise RuntimeError(msg)
