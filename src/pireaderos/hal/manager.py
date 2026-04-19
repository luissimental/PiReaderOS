import logging
import threading
from collections.abc import Callable, Sequence
from typing import Self

import gpiozero
import smbus2

logger = logging.getLogger(__name__)


I2C_BUS = 3


class GPIOPin:  # pragma: no cover
    """GPIO pin wrapper."""

    def __init__(
        self,
        pin_number: int,
        device: gpiozero.DigitalInputDevice | gpiozero.DigitalOutputDevice,
    ) -> None:
        self._pin_number = pin_number
        self._device = device

    @property
    def pin_number(self) -> int:
        """The pin number that the device is connected to."""
        return self._pin_number

    @property
    def closed(self) -> bool:
        """Returns `True` if the device is closed."""
        return self._device.closed

    def on(self) -> None:
        """Turn the device on."""
        if isinstance(self._device, gpiozero.DigitalOutputDevice):
            self._device.on()

    def off(self) -> None:
        """Turn the device off."""
        if isinstance(self._device, gpiozero.DigitalOutputDevice):
            self._device.off()

    def set_when_activated(self, callback: Callable) -> None:
        """Run callback function when device is activated."""
        self._device.when_activated = callback

    def _close(self) -> None:
        """Shuts down the device and releases all associated resources.

        Use `HardwareManager.release_pin` for closing.
        """
        self._device.close()


class HardwareManager:
    """Central location to manage Raspberry PI GPIO pin hardware.

    Best used as a context manager for graceful clean up during exceptions.
    """

    def __init__(self) -> None:
        self._i2c = smbus2.SMBus(I2C_BUS)
        self._active_pins: dict[int, GPIOPin] = {}

        self._pin_lock = threading.Lock()
        self._i2c_lock = threading.Lock()

        self._closed = False  # Flag for detecting clean up

        logger.info("Initialized 'HardwareManager'")

    def request_pin(
        self, pin: int, mode: str, *, pull_up: bool = False
    ) -> GPIOPin:
        """Request a pin from the device.

        Pin must be closed using `HardwareManager.release_pin`.

        Args:
          pin:
            The GPIO pin number
          mode:
            Must be one of 'input' or 'output'.
          pull_up:
            The pin will be pulled up if True.

        """
        self._ensure_open()

        with self._pin_lock:
            if pin in self._active_pins:
                logger.error("GPIO pin %s already allocated", pin)
                msg = f"GPIO pin {pin} already allocated"
                raise RuntimeError(msg)

            if mode == "input":
                device = GPIOPin(
                    pin, gpiozero.DigitalInputDevice(pin, pull_up=pull_up)
                )
            elif mode == "output":
                device = GPIOPin(pin, gpiozero.DigitalOutputDevice(pin))
            else:
                logger.error("Unknown mode: '%s'", mode)
                msg_0 = f"Unknown mode: {mode}"
                raise ValueError(msg_0)

            self._active_pins[pin] = device
            return device

    def release_pin(self, pin: GPIOPin) -> None:
        """Shut down the device and release all associated resources."""
        self._ensure_open()

        device = None
        pin_number = pin.pin_number
        with self._pin_lock:
            device = self._active_pins.pop(pin_number, None)

        if not device:
            logger.error("Pin %s already released", pin_number)
            msg = f"Pin {pin_number} already released"
            raise RuntimeError(msg)
        device._close()

    def i2c_read_byte_data(self, i2c_addr: int, reg: int) -> int:
        """Read a single byte from a given register.

        Args:
          i2c_addr:
            The i2c address.
          reg:
            The start register.

        Returns:
            The read byte value.

        """
        self._ensure_open()
        with self._i2c_lock:
            return self._i2c.read_byte_data(i2c_addr, reg)

    def i2c_read_block_data(
        self, i2c_addr: int, reg: int, length: int = 1
    ) -> list[int]:
        """Read a block of byte data from a given register.

        Args:
          i2c_addr:
            The i2c address.
          reg:
            The start register.
          length:
            The desired block length.

        Returns:
            The list of bytes.

        """
        self._ensure_open()

        if length >= 1:
            with self._i2c_lock:
                return self._i2c.read_i2c_block_data(i2c_addr, reg, length)
        else:
            logger.error("Length %s must be at least 1", length)
            msg = f"Length {length} must be at least 1"
            raise ValueError(msg)

    def i2c_write(
        self, i2c_addr: int, reg: int, data: int | Sequence[int]
    ) -> None:
        """Write a byte or a block of byte data to a given register.

        Args:
          i2c_addr:
            The i2c address.
          reg:
            The register to write to.
          data:
            The byte value or list of bytes to transmit.

        """
        self._ensure_open()

        with self._i2c_lock:
            if isinstance(data, int):
                self._i2c.write_byte_data(i2c_addr, reg, data)
            else:
                self._i2c.write_block_data(i2c_addr, reg, data)

    def clean_up(self) -> None:
        """Release all GPIO pins and the i2c bus."""
        if self._closed:
            return

        with self._pin_lock:
            devices = list(self._active_pins.values())
            self._active_pins.clear()

        for device in devices:
            device._close()

        with self._i2c_lock:
            self._i2c.close()

        self._closed = True

    def _ensure_open(self) -> None:
        if self._closed:
            logger.error("'HardwareManager' is closed")
            msg = "HardwareManager is closed"
            raise RuntimeError(msg)

    def __enter__(self) -> Self:
        """Enter as a context manager."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        """Exit context manager."""
        self.clean_up()
