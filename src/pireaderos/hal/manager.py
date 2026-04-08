import logging
from threading import Lock
from typing import Callable, Sequence

import smbus2
from gpiozero import DigitalInputDevice, DigitalOutputDevice


logger = logging.getLogger(__name__)

I2C_BUS = 3


class GPIOPin:  # pragma: no cover
    """GPIO pin wrapper"""

    def __init__(self, pin_number: int, device):
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

    def on(self):
        """Turns the device on."""
        self._device.on()

    def off(self):
        """Turns the device off."""
        self._device.off()

    def set_when_activated(self, callback: Callable):
        """Runs callback function when device is activated."""
        self._device.when_activated = callback

    def _close(self):
        """Shuts down the device and releases all associated resources.

        Use `HardwareManager.release_pin` for closing.
        """
        self._device.close()


class HardwareManager:
    """Central location to manage Raspberry PI GPIO pin hardware.

    Best used as a context manager for graceful clean up during exceptions.
    """

    def __init__(self):
        self._i2c = smbus2.SMBus(I2C_BUS)
        self._active_pins: dict[int, GPIOPin] = {}

        self._pin_lock = Lock()
        self._i2c_lock = Lock()

        self._closed = False  # Flag for detecting clean up

        logger.info("Initialized 'HardwareManager'")

    def request_pin(self, pin: int, mode: str, **kwargs):
        """Requests a pin from the device.

        Args:
            pin (int): GPIO pin number
            mode (str): Must be one of 'input' or 'output'
            kwargs: Standard kwargs for gpiozero
                `DigitalInputDevice` or `DigitalOutputDevice`

        Note: pin must be closed using `HardwareManager.release_pin`.
        """
        self._ensure_open()

        with self._pin_lock:
            if pin in self._active_pins:
                logger.error(f"GPIO pin {pin} already allocated")
                raise RuntimeError(f"GPIO pin {pin} already allocated")

            if mode == "input":
                device = GPIOPin(pin, DigitalInputDevice(pin, **kwargs))
            elif mode == "output":
                device = GPIOPin(pin, DigitalOutputDevice(pin, **kwargs))
            else:
                logger.error(f"Unknown mode: '{mode}'")
                raise ValueError(f"Unknown mode: {mode}")

            self._active_pins[pin] = device
            return device

    def release_pin(self, pin: GPIOPin):
        """Shuts down the device and releases all associated resources."""
        self._ensure_open()

        device = None
        pin_number = pin.pin_number
        with self._pin_lock:
            device = self._active_pins.pop(pin_number, None)

        if not device:
            logger.error(f"Pin {pin_number} already released")
            raise RuntimeError(f"Pin {pin_number} already released")
        device._close()

    def i2c_read_byte_data(self, i2c_addr: int, reg: int):
        """Reads a single byte from a given register.

        Args:
            i2c_addr (int): i2c address
            reg (int): Start register

        Returns:
            int: Read byte value
        """
        self._ensure_open()
        with self._i2c_lock:
            return self._i2c.read_byte_data(i2c_addr, reg)

    def i2c_read_block_data(self, i2c_addr: int, reg: int, length=1):
        """Reads a block of byte data from a given register.

        Args:
            i2c_addr (int): i2c address
            reg (int): Start register
            length (int): Desired block length

        Returns:
            list: List of bytes
        """
        self._ensure_open()

        if length >= 1:
            with self._i2c_lock:
                return self._i2c.read_i2c_block_data(i2c_addr, reg, length)
        else:
            logger.error(f"Length {length} must be at least 1")
            raise ValueError(f"Length {length} must be at least 1")

    def i2c_write(self, i2c_addr: int, reg: int, data: int | Sequence[int]):
        """Writes a byte or a block of byte data to a given register.

        Args:
            i2c_addr (int): i2c address
            reg (int): Register to write to
            data (int | Sequence[int]): Byte value or list of bytes to transmit
        """
        self._ensure_open()

        with self._i2c_lock:
            if isinstance(data, int):
                self._i2c.write_byte_data(i2c_addr, reg, data)
            else:
                self._i2c.write_block_data(i2c_addr, reg, data)

    def clean_up(self):
        """Releases all GPIO pins and i2c bus."""
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

    def _ensure_open(self):
        if self._closed:
            logger.error("'HardwareManager' is closed")
            raise RuntimeError("HardwareManager is closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.clean_up()
