from typing import override

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import base

behavior_action = base.behavior_action


class HoldBehavior(base.BaseBehavior):
    """The behavior for the hold gesture."""

    @override
    def __init__(
        self,
        *,
        on_touch_down: base.BehaviorAction | None = None,
        on_hold: base.BehaviorAction | None = None,
        on_release: base.BehaviorAction | None = None,
    ) -> None:
        """Initialize the HoldBehavior object.

        Args:
          on_touch_down:
            The optional callback for touch down events. Must accept the owning
            component. Can accept the dispatched gesture if needed.
          on_hold:
            The optional callback for hold events. Must accept the owning
            component. Can accept the dispatched gesture if needed.
          on_release:
            The optional callback for release events. Must accept the owning
            component. Can accept the dispatched gesture if needed.

        """
        super().__init__(on_touch_down=on_touch_down, on_release=on_release)
        self._on_hold_callback = on_hold

    @override
    def handle_gesture(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        super().handle_gesture(owner, gesture)

        if gesture.type is enums.GestureType.HOLD and self._is_active:
            self._on_hold(owner, gesture)
            self._is_active = False

    def _on_hold(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        """Handle the hold gesture."""
        if self._on_hold_callback is not None:
            self._safe_call(self._on_hold_callback, owner, gesture)
