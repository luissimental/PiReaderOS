from typing import override

from pireaderos.common import enums, models
from pireaderos.ui.behavior import base


class ZoomAndRotateBehavior(base.BaseBehavior):
    """The behavior for the zoom and rotate gesture."""

    def __init__(
        self,
        *,
        on_zoom_and_rotate: base.OptionalCallback = None,
        on_release: base.OptionalCallback = None,
    ) -> None:
        """Initialize the ZoomAndRotateBehavior object.

        Args:
          on_zoom_and_rotate:
            The optional callback for zoom and rotate events. Must accept a
            GestureEvent.
          on_release:
            The optional callback for multi-touch release events. Must accept a
            GestureEvent.

        """
        self._on_zoom_and_rotate_callback = on_zoom_and_rotate
        self._on_release_callback = on_release
        self._is_active = False

    @override
    def handle_gesture(self, gesture: models.GestureEvent) -> None:
        if gesture.type is enums.GestureType.ZOOM_AND_ROTATE:
            self._on_zoom_and_rotate(gesture)
            self._is_active = True

        if (
            gesture.type is enums.GestureType.MULTI_TOUCH_RELEASE
            and self._is_active
        ):
            self._on_release(gesture)
            self._is_active = False

    def _on_zoom_and_rotate(self, gesture: models.GestureEvent) -> None:
        """Handle zoom and rotate gesture."""
        if self._on_zoom_and_rotate_callback is not None:
            self._on_zoom_and_rotate_callback(gesture)

    def _on_release(self, gesture: models.GestureEvent) -> None:
        """Handle multi-touch release gesture."""
        if self._on_release_callback is not None:
            self._on_release_callback(gesture)
