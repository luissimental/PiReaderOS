from typing import override

from pireaderos.common import models
from pireaderos.input import enums
from pireaderos.ui.behavior import base


class DelayedTapBehavior(base.BaseBehavior):
    """The behavior for the delayed tap gesture."""

    def __init__(self, *, on_tap: base.OptionalCallback = None) -> None:
        """Initialize the DelayedTapBehavior object.

        Args:
          on_tap:
            The optional callback for delayed tap events. Must accept a
            GestureEvent.

        """
        self._on_tap_callback = on_tap

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        if gesture.type is enums.GestureType.DELAYED_TAP:
            self._on_tap(gesture)

    def _on_tap(self, gesture: models.GestureEvent) -> None:
        """Handle the delayed tap gesture."""
        if self._on_tap_callback is not None:
            self._on_tap_callback(gesture)
