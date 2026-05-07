from typing import override

from pireaderos.common import models
from pireaderos.input import enums
from pireaderos.ui.behavior import base


class TapBehavior(base.BaseBehavior):
    """The behavior for the tap gesture."""

    def __init__(self, *, on_tap: base.OptionalCallback = None) -> None:
        """Initialize the TapBehavior object.

        Args:
          on_tap:
            The optional callback for tap events. Must accept a GestureEvent.

        """
        self._on_tap_callback = on_tap

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        if gesture.type is enums.GestureType.TAP:
            self._on_tap(gesture)

    def _on_tap(self, gesture: models.GestureEvent) -> None:
        """Handle the tap gesture."""
        if self._on_tap_callback is not None:
            self._on_tap_callback(gesture)
