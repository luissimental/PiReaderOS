from typing import override

from pireaderos.common import enums, models
from pireaderos.ui.behavior import base


class HoldBehavior(base.BaseBehavior):
    """The behavior for the hold gesture."""

    def __init__(
        self,
        *,
        on_touch_down: base.OptionalCallback = None,
        on_hold: base.OptionalCallback = None,
        on_release: base.OptionalCallback = None,
    ) -> None:
        """Initialize the HoldBehavior object.

        Args:
          on_touch_down:
            The optional callback for touch down events. Must accept a
            GestureEvent.
          on_hold:
            The optional callback for hold events. Must accept a GestureEvent.
          on_release:
            The optional callback for release events. Must accept a
            GestureEvent.

        """
        super().__init__(on_touch_down=on_touch_down, on_release=on_release)
        self._on_hold_callback = on_hold

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        super().handle_gesture(gesture)

        if gesture.type is enums.GestureType.HOLD and self._is_active:
            self._on_hold(gesture)
            self._is_active = False

    def _on_hold(self, gesture: models.GestureEvent) -> None:
        """Handle the hold gesture."""
        if self._on_hold_callback is not None:
            self._on_hold_callback(gesture)
