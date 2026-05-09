from typing import override

from pireaderos.common import models
from pireaderos.ui import component
from pireaderos.ui.behavior import base

behavior_action = base.behavior_action


class TouchDownBehavior(base.BaseBehavior):
    """The behavior for the touch down gesture."""

    @override
    def __init__(
        self,
        *,
        on_touch_down: base.BehaviorAction | None = None,
        on_release: base.BehaviorAction | None = None,
    ) -> None:
        """Initialize the TouchDownBehavior object.

        Args:
          on_touch_down:
            The optional callback for touch down events. Must accept the owning
            component. Can accept the dispatched gesture if needed.
          on_release:
            The optional callback for release events. Must accept the owning
            component. Can accept the dispatched gesture if needed.

        """
        super().__init__(on_touch_down=on_touch_down, on_release=on_release)

    @override
    def handle_gesture(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        super().handle_gesture(owner, gesture)
