from typing import override

from pireaderos.common import enums, models
from pireaderos.ui.behavior import base


class MultiTouchHoldBehavior(base.BaseBehavior):
    """The behavior for the multi-touch hold gesture."""

    def __init__(
        self,
        *,
        on_hold: base.OptionalCallback = None,
        on_release: base.OptionalCallback = None,
    ) -> None:
        """Initialize the MultiTouchHoldBehavior object.

        Args:
          on_hold:
            The optional callback for multi-touch hold events. Must accept a
            GestureEvent.
          on_release:
            The optional callback for multi-touch release events. Must accept a
            GestureEvent.

        """
        self._on_hold_callback = on_hold
        self._on_release_callback = on_release
        self.is_active = False

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        if (
            gesture.type is enums.GestureType.MULTI_TOUCH_HOLD
            and not self.is_active
        ):
            self._on_hold(gesture)
            self.is_active = True

        if (
            gesture.type is enums.GestureType.MULTI_TOUCH_RELEASE
            and self.is_active
        ):
            self._on_release(gesture)
            self.is_active = False

    def _on_hold(self, gesture: models.GestureEvent) -> None:
        """Handle the multi-touch hold gesture."""
        if self._on_hold_callback is not None:
            self._on_hold_callback(gesture)

    def _on_release(self, gesture: models.GestureEvent) -> None:
        """Handle the multi-touch release gesture."""
        if self._on_release_callback is not None:
            self._on_release_callback(gesture)
