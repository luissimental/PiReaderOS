from typing import override

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import base

behavior_action = base.behavior_action


class ZoomAndRotateBehavior(base.BaseBehavior):
    """The behavior for the zoom and rotate gesture."""

    @override
    def __init__(
        self,
        *,
        on_zoom_and_rotate: base.BehaviorAction | None = None,
        on_release: base.BehaviorAction | None = None,
    ) -> None:
        """Initialize the ZoomAndRotateBehavior object.

        Args:
          on_zoom_and_rotate:
            The optional callback for zoom and rotate events. Must accept the
            owning component. Can accept the dispatched gesture if needed.
          on_release:
            The optional callback for multi-touch release events. Must accept
            the owning component. Can accept the dispatched gesture if needed.

        """
        self._on_zoom_and_rotate_callback = on_zoom_and_rotate
        self._on_release_callback = on_release
        self._is_active = False

    @override
    def handle_gesture(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        if gesture.type is enums.GestureType.ZOOM_AND_ROTATE:
            self._on_zoom_and_rotate(owner, gesture)
            self._is_active = True

        if (
            gesture.type is enums.GestureType.MULTI_TOUCH_RELEASE
            and self._is_active
        ):
            self._on_release(owner, gesture)
            self._is_active = False

    def _on_zoom_and_rotate(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        """Handle zoom and rotate gesture."""
        if self._on_zoom_and_rotate_callback is not None:
            self._safe_call(self._on_zoom_and_rotate_callback, owner, gesture)

    def _on_release(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        """Handle multi-touch release gesture."""
        if self._on_release_callback is not None:
            self._safe_call(self._on_release_callback, owner, gesture)
