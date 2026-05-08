from typing import override

from pireaderos.common import models
from pireaderos.ui.behavior import base


class TouchDownBehavior(base.BaseBehavior):
    """The behavior for the touch down gesture."""

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        super().handle_gesture(gesture)
