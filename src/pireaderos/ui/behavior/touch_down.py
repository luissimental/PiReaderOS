from typing import override

from pireaderos.input import enums, models
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
        self._on_touch_down_callback = on_touch_down
        self._on_release_callback = on_release
        self._is_active = False

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        if (
            gesture.type is enums.GestureType.TOUCH_DOWN
            and not self._is_active
        ):
            self._on_touch_down(gesture)
            self._is_active = True

        if gesture.type is enums.GestureType.RELEASE and self._is_active:
            self._on_release(gesture)
            self._is_active = False

    def _on_touch_down(self, gesture: models.GestureEvent) -> None:
        """Handle the touch down gesture."""
        if self._on_touch_down_callback is not None:
            self._on_touch_down_callback(gesture)

    def _on_release(self, gesture: models.GestureEvent) -> None:
        """Handle the release gesture."""
        if self._on_release_callback is not None:
            self._on_release_callback(gesture)
