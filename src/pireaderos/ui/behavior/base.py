# pragma: exclude file
import abc
import inspect
from collections.abc import Callable
from typing import Any, Protocol, overload

from pireaderos.common import enums, models
from pireaderos.ui import component

BaseComponentHandler = Callable[[component.Component], Any]
UnaryGestureHandler = Callable[[component.Component, models.GestureEvent], Any]


class BehaviorAction(Protocol):
    """The call signatures for the behavior action."""

    @overload
    def __call__(self, owner: component.Component, /) -> None: ...
    @overload
    def __call__(
        self, owner: component.Component, gesture: models.GestureEvent, /
    ) -> None: ...


@overload
def behavior_action(function: BaseComponentHandler) -> BehaviorAction: ...
@overload
def behavior_action(function: UnaryGestureHandler) -> BehaviorAction: ...
def behavior_action(function: Callable) -> BehaviorAction:
    """Mark function as a behavior action."""
    sig = inspect.signature(function)

    setattr(function, "_params_count", len(sig.parameters))
    return function


class BaseBehavior(abc.ABC):
    """The base class for all gesture behaviors."""

    @abc.abstractmethod
    def __init__(
        self,
        *,
        on_touch_down: BehaviorAction | None = None,
        on_release: BehaviorAction | None = None,
    ) -> None:
        self._on_touch_down_callback = on_touch_down
        self._on_release_callback = on_release
        self._is_active = False

    @abc.abstractmethod
    def handle_gesture(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        """Dispatch gesture to handler method."""
        if (
            gesture.type is enums.GestureType.TOUCH_DOWN
            and not self._is_active
        ):
            self._on_touch_down(owner, gesture)
            self._is_active = True

        elif gesture.type is enums.GestureType.RELEASE and self._is_active:
            self._on_release(owner, gesture)
            self._is_active = False

    def _safe_call(
        self,
        listener: BehaviorAction,
        owner: component.Component,
        gesture: models.GestureEvent,
    ) -> None:
        """Call listener with correct arguments."""
        count = getattr(listener, "_params_count", 2)

        if count == 2:
            listener(owner, gesture)
        else:
            listener(owner)

    def _on_touch_down(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        """Handle the touch down gesture."""
        if self._on_touch_down_callback is not None:
            self._safe_call(self._on_touch_down_callback, owner, gesture)

    def _on_release(
        self, owner: component.Component, gesture: models.GestureEvent
    ) -> None:
        """Handle the release gesture."""
        if self._on_release_callback is not None:
            self._safe_call(self._on_release_callback, owner, gesture)
