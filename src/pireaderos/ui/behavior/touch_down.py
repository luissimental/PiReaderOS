from typing import override

from pireaderos.common import models
from pireaderos.ui.behavior import base


class TouchDownBehavior(base.BaseBehavior):
    """The behavior for the touch down gesture."""

    def __init__(
        self,
        *,
        on_touch_down: base.OptionalCallback = None,
        on_release: base.OptionalCallback = None,
    ) -> None:
        """Initialize the TouchDownBehavior object.

        Args:
          on_touch_down:
            The optional callback for touch down events. Must accept a
            GestureEvent.
          on_release:
            The optional callback for release events. Must accept a
            GestureEvent.

        """
        super().__init__(on_touch_down=on_touch_down, on_release=on_release)

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        super().handle_gesture(gesture)
