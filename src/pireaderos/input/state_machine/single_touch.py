import statemachine

from pireaderos.common import models
from pireaderos.input import constants, enums, geometry


class SingleTouchStateMachine(statemachine.StateChart):
    """Finite state machine for processing raw touch data into gestures.

    This state machine only processes one touch point at a time, so any extra
    fingers on the screen require a separate instance of this class.
    Multi-touch gestures can be generated using the `MultiTouchStateMachine`
    class.

    Example:
      Initialize the state machine and generate a gesture from a point::

        point: TouchPoint | None = ...
        single_touch = SingleTouchStateMachine()
        gesture = single_touch.generate_gesture(point)

    """

    # States
    idle = statemachine.State(initial=True)
    down = statemachine.State()
    contact = statemachine.State()
    holding = statemachine.State()
    dragging = statemachine.State()

    # Events and transitions
    touch_down = down.from_(idle)
    touch_contact = contact.from_(down, contact)
    hold = holding.from_(contact, holding, cond="_should_hold")
    drag = dragging.from_(holding, dragging, cond="_should_drag")
    release = idle.from_(down, contact, holding, dragging)

    def __init__(self) -> None:
        super().__init__()
        self._start_point: models.TouchPoint | None = None
        self._last_point: models.TouchPoint | None = None

    def generate_gesture(
        self, point: models.TouchPoint | None
    ) -> models.GestureEvent | None:
        """Process touch point to generate a gesture.

        Args:
          point:
            The touch point to be processed. Point is None when the finger
            lifts from the screen.

        Returns:
          The gesture after processing. The gesture may be None if the current
          state did not detect a valid gesture yet.

        """
        if point is None:
            if self.release in self.allowed_events:
                return self.release()
            return None

        if self.touch_down in self.allowed_events:
            return self.touch_down(point)
        if self.hold in self.enabled_events(point):
            return self.hold(point)
        if self.drag in self.enabled_events(point):
            return self.drag(point)
        if self.touch_contact in self.allowed_events:
            return self.touch_contact(point)

        return None  # pragma: no cover

    def _should_hold(self, point: models.TouchPoint) -> bool:
        if self._start_point is None:  # pragma: no cover
            return False

        duration = geometry.get_duration(point, self._start_point)
        distance = geometry.get_distance(point, self._start_point)

        return (
            duration >= constants.GestureThreshold.HOLD_TIME
            and distance < constants.GestureThreshold.HOLD_DISTANCE
        )

    def _should_drag(self, point: models.TouchPoint) -> bool:
        if self._start_point is None:  # pragma: no cover
            return False
        if self.dragging.is_active:
            return True

        distance = geometry.get_distance(point, self._start_point)
        return distance >= constants.GestureThreshold.DRAG_DISTANCE

    def on_touch_down(self, point: models.TouchPoint) -> models.GestureEvent:
        """Set the start point and generate the touch down gesture."""
        self._start_point = point

        return models.GestureEvent(
            type=enums.GestureType.TOUCH_DOWN,
            start_point=point,
            end_point=point,
        )

    def on_hold(self, point: models.TouchPoint) -> models.GestureEvent | None:
        """Generate the hold gesture."""
        if self._start_point is None:  # pragma: no cover
            return None

        return models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=self._start_point,
            end_point=point,
        )

    def on_drag(self, point: models.TouchPoint) -> models.GestureEvent | None:
        """Generate the drag gesture."""
        if self._start_point is None:  # pragma: no cover
            return None

        return models.GestureEvent(
            type=enums.GestureType.DRAG,
            start_point=self._start_point,
            end_point=point,
        )

    def on_release(
        self, source: statemachine.State
    ) -> models.GestureEvent | None:
        """Generate a tap, swipe, or release gesture based on the context."""
        if (  # pragma: no cover
            self._start_point is None or self._last_point is None
        ):
            return None

        duration = geometry.get_duration(self._last_point, self._start_point)
        distance = geometry.get_distance(self._last_point, self._start_point)

        # Tap gesture
        if (
            duration < constants.GestureThreshold.TAP_TIME
            and distance < constants.GestureThreshold.TAP_DISTANCE
        ):
            return models.GestureEvent(
                type=enums.GestureType.TAP,
                start_point=self._start_point,
                end_point=self._last_point,
            )
        # Swipe gesture
        if (
            duration < constants.GestureThreshold.SWIPE_TIME
            and distance >= constants.GestureThreshold.SWIPE_DISTANCE
        ):
            dx, dy = geometry.get_deltas(self._last_point, self._start_point)
            if abs(dx) > abs(dy):
                direction = (
                    enums.SwipeDirection.RIGHT
                    if dx > 0
                    else enums.SwipeDirection.LEFT
                )
            else:
                direction = (
                    enums.SwipeDirection.DOWN
                    if dy > 0
                    else enums.SwipeDirection.UP
                )

            return models.GestureEvent(
                type=enums.GestureType.SWIPE,
                start_point=self._start_point,
                end_point=self._last_point,
                swipe_direction=direction,
            )
        # Release gesture for selected states
        if source in (self.holding, self.dragging, self.contact):
            return models.GestureEvent(
                type=enums.GestureType.RELEASE,
                start_point=self._start_point,
                end_point=self._last_point,
            )

        return None  # pragma: no cover

    def after_transition(self, point: models.TouchPoint) -> None:
        """Set the last point after a transition."""
        self._last_point = point
