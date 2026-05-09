from typing import override

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import base

behavior_action = base.behavior_action


class TapBehavior(base.BaseBehavior):
    """The behavior for the tap gesture."""

    @override
    def __init__(self, *, on_tap: base.BehaviorAction | None = None) -> None:
        """Initialize the TapBehavior object.

        Args:
          on_tap:
            The optional callback for tap events. Must accept the owning
            component. Can accept the dispatched gesture if needed.

        """
        self._on_tap_callback = on_tap

    @override
    def handle_gesture(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        if gesture.type is enums.GestureType.TAP:
            self._on_tap(owner, gesture)

    def _on_tap(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        """Handle the tap gesture."""
        if self._on_tap_callback is not None:
            self._safe_call(self._on_tap_callback, owner, gesture)
