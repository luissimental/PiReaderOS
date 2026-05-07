from typing import override

from pireaderos.input import enums, models
from pireaderos.ui.behavior import base


class HoldBehavior(base.BaseBehavior):
    """The behavior for the hold gesture."""

    def __init__(
        self,
        *,
        on_hold: base.OptionalCallback = None,
        on_release: base.OptionalCallback = None,
    ) -> None:
        """Initialize the HoldBehavior object.

        Args:
          on_hold:
            The optional callback for hold events. Must accept a GestureEvent.
          on_release:
            The optional callback for release events. Must accept a
            GestureEvent.

        """
        self._on_hold_callback = on_hold
        self._on_release_callback = on_release
        self._is_holding = False

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        if gesture.type is enums.GestureType.HOLD and not self._is_holding:
            self._on_hold(gesture)
            self._is_holding = True

        if gesture.type is enums.GestureType.RELEASE and self._is_holding:
            self._on_release(gesture)
            self._is_holding = False

    def _on_hold(self, gesture: models.GestureEvent) -> None:
        """Handle the hold gesture."""
        if self._on_hold_callback is not None:
            self._on_hold_callback(gesture)

    def _on_release(self, gesture: models.GestureEvent) -> None:
        """Handle the release gesture."""
        if self._on_release_callback is not None:
            self._on_release_callback(gesture)
