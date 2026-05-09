from typing import override

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import base

behavior_action = base.behavior_action


class SwipeBehavior(base.BaseBehavior):
    """The behavior for the swipe gesture."""

    @override
    def __init__(self, *, on_swipe: base.BehaviorAction | None = None) -> None:
        """Initialize the SwipeBehavior object.

        Args:
          on_swipe:
            The optional callback for swipe events. Must accept the owning
            component. Can accept the dispatched gesture if needed.

        """
        self._on_swipe_callback = on_swipe

    @override
    def handle_gesture(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        if gesture.type is enums.GestureType.SWIPE:
            self._on_swipe(owner, gesture)

    def _on_swipe(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        if self._on_swipe_callback is not None:
            self._safe_call(self._on_swipe_callback, owner, gesture)
