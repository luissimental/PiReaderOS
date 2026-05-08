from typing import override

from pireaderos.common import enums, models
from pireaderos.ui.behavior import base


class DragBehavior(base.BaseBehavior):
    """The behavior for the drag gesture."""

    def __init__(
        self,
        *,
        on_touch_down: base.OptionalCallback = None,
        on_drag: base.OptionalCallback = None,
        on_release: base.OptionalCallback = None,
    ) -> None:
        """Initialize the DragBehavior object.

        Args:
          on_touch_down:
            The optional callback for touch down events. Must accept a
            GestureEvent.
          on_drag:
            The optional callback for drag events. Must accept a GestureEvent.
          on_release:
            The optional callback for release events. Must accept a
            GestureEvent.

        """
        super().__init__(on_touch_down=on_touch_down, on_release=on_release)
        self._on_drag_callback = on_drag

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        super().handle_gesture(gesture)

        if gesture.type is enums.GestureType.DRAG and self._is_active:
            self._on_drag(gesture)

    def _on_drag(self, gesture: models.GestureEvent) -> None:
        """Handle the drag gesture."""
        if self._on_drag_callback is not None:
            self._on_drag_callback(gesture)
