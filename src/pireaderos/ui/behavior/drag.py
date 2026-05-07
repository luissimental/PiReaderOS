from typing import override

from pireaderos.input import enums, models
from pireaderos.ui.behavior import base


class DragBehavior(base.BaseBehavior):
    """The behavior for the drag gesture."""

    def __init__(
        self,
        *,
        on_drag: base.OptionalCallback = None,
        on_release: base.OptionalCallback = None,
    ) -> None:
        """Initialize the DragBehavior object.

        Args:
          on_drag:
            The optional callback for drag events. Must accept a GestureEvent.
          on_release:
            The optional callback for release events. Must accept a
            GestureEvent.

        """
        self._on_drag_callback = on_drag
        self._on_release_callback = on_release
        self._is_dragging = False

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        if gesture.type is enums.GestureType.DRAG and not self._is_dragging:
            self._on_drag(gesture)
            self._is_dragging = True

        if gesture.type is enums.GestureType.RELEASE and self._is_dragging:
            self._on_release(gesture)
            self._is_dragging = False

    def _on_drag(self, gesture: models.GestureEvent) -> None:
        """Handle the drag gesture."""
        if self._on_drag_callback is not None:
            self._on_drag_callback(gesture)

    def _on_release(self, gesture: models.GestureEvent) -> None:
        """Handle the release gesture."""
        if self._on_release_callback is not None:
            self._on_release_callback(gesture)
