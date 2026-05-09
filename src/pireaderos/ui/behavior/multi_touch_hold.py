from typing import override

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import base

behavior_action = base.behavior_action


class MultiTouchHoldBehavior(base.BaseBehavior):
    """The behavior for the multi-touch hold gesture."""

    @override
    def __init__(
        self,
        *,
        on_hold: base.BehaviorAction | None = None,
        on_release: base.BehaviorAction | None = None,
    ) -> None:
        """Initialize the MultiTouchHoldBehavior object.

        Args:
          on_hold:
            The optional callback for multi-touch hold events. Must accept the
            owning component. Can accept the dispatched gesture if needed.
          on_release:
            The optional callback for multi-touch release events. Must accept
            the owning component. Can accept the dispatched gesture if needed.

        """
        self._on_hold_callback = on_hold
        self._on_release_callback = on_release
        self.is_active = False

    @override
    def handle_gesture(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        if (
            gesture.type is enums.GestureType.MULTI_TOUCH_HOLD
            and not self.is_active
        ):
            self._on_hold(owner, gesture)
            self.is_active = True

        if (
            gesture.type is enums.GestureType.MULTI_TOUCH_RELEASE
            and self.is_active
        ):
            self._on_release(owner, gesture)
            self.is_active = False

    def _on_hold(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        """Handle the multi-touch hold gesture."""
        if self._on_hold_callback is not None:
            self._safe_call(self._on_hold_callback, owner, gesture)

    def _on_release(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        """Handle the multi-touch release gesture."""
        if self._on_release_callback is not None:
            self._safe_call(self._on_release_callback, owner, gesture)
