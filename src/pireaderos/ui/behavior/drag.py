from typing import override

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import base

behavior_action = base.behavior_action


class DragBehavior(base.BaseBehavior):
    """The behavior for the drag gesture."""

    @override
    def __init__(
        self,
        *,
        on_touch_down: base.BehaviorAction | None = None,
        on_drag: base.BehaviorAction | None = None,
        on_release: base.BehaviorAction | None = None,
    ) -> None:
        """Initialize the DragBehavior object.

        Args:
          on_touch_down:
            The optional callback for touch down events. Must accept the owning
            component. Can accept the dispatched gesture if needed.
          on_drag:
            The optional callback for drag events. Must accept the owning
            component. Can accept the dispatched gesture if needed.
          on_release:
            The optional callback for release events. Must accept the owning
            component. Can accept the dispatched gesture if needed.

        """
        super().__init__(on_touch_down=on_touch_down, on_release=on_release)
        self._on_drag_callback = on_drag

    @override
    def handle_gesture(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        super().handle_gesture(owner, gesture)

        if gesture.type is enums.GestureType.DRAG and self._is_active:
            self._on_drag(owner, gesture)

    def _on_drag(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        """Handle the drag gesture."""
        if self._on_drag_callback is not None:
            self._safe_call(self._on_drag_callback, owner, gesture)
