from typing import override

from pireaderos.input import enums, models
from pireaderos.ui.behavior import base


class SwipeBehavior(base.BaseBehavior):
    """The behavior for the swipe gesture."""

    def __init__(self, *, on_swipe: base.OptionalCallback = None) -> None:
        """Initialize the SwipeBehavior object.

        Args:
          on_swipe:
            The optional callback for swipe events. Must accept a GestureEvent.

        """
        self._on_swipe_callback = on_swipe

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        if gesture.type is enums.GestureType.SWIPE:
            self._on_swipe(gesture)

    def _on_swipe(self, gesture: models.GestureEvent) -> None:
        if self._on_swipe_callback is not None:
            self._on_swipe_callback(gesture)
