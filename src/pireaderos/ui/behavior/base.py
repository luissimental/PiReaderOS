# pragma: exclude file
import abc
from collections.abc import Callable
from typing import Any

from pireaderos.common import models

OptionalCallback = Callable[[models.GestureEvent], Any] | None


class BaseBehavior(abc.ABC):
    """The base class for all gesture behaviors."""

    @abc.abstractmethod
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        """Dispatch gesture to handler method."""
