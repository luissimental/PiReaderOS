import math

import statemachine

from pireaderos.common import models
from pireaderos.input import constants, enums, geometry


class MultiTouchStateMachine(statemachine.StateChart):
    """Finite state machine for processing multi-touch gestures.

    This state machine processes two single-touch gestures from
    `SingleTouchStateMachine` and generates a multi-touch gesture.

    Example:
      Initialize the state machine and generate a multi-touch gesture from two
      single-touch gestures::

        single_touch1: GestureEvent | None = ...
        single_touch2: GestureEvent | None = ...
        multi_touch = MultiTouchStateMachine()
        gesture = multi_touch.generate_gesture(single_touch1, single_touch2)

    """

    # States
    idle = statemachine.State(initial=True)
    two_fingers_down = statemachine.State()
    transforming = statemachine.State()

    # Events and transitions
    start = two_fingers_down.from_(idle, cond="_should_start")
    activate = transforming.from_(two_fingers_down, cond="_should_activate")
    update = transforming.from_.itself()
    end = idle.from_(two_fingers_down, transforming, cond="_should_end")

    def __init__(self) -> None:
        super().__init__()
        self._start_distance: float = 0.0
        self._start_angle: float = 0.0

    def generate_gesture(
        self,
        gesture1: models.GestureEvent | None,
        gesture2: models.GestureEvent | None,
    ) -> models.GestureEvent | None:
        """Process single-touch gestures to generate a multi-touch gesture.

        Args:
          gesture1:
            The first single-touch gesture to be processed. May be None when
            the single-touch gesture is not a detected gesture yet.
          gesture2:
            The second single-touch gesture to be processed. May be None when
            the single-touch gesture is not a detected gesture yet.

        Returns:
          The multi-touch gesture after processing. May be None when the state
          machine did not detect a multi-touch gesture yet.

        """
        if gesture1 is None or gesture2 is None:
            return None

        if self.start in self.enabled_events(gesture1, gesture2):
            return self.start(gesture1, gesture2)
        if self.activate in self.enabled_events(gesture1, gesture2):
            self.activate(gesture1, gesture2)  # State transition only
        if self.end in self.enabled_events(gesture1, gesture2):
            return self.end(gesture1, gesture2)

        # Update is called after activation
        if self.update in self.allowed_events:
            return self.update(gesture1, gesture2)

        return None

    def _should_start(
        self, gesture1: models.GestureEvent, gesture2: models.GestureEvent
    ) -> bool:
        """Both gestures must be one of hold or drag types to start."""
        types = (enums.GestureType.HOLD, enums.GestureType.DRAG)
        return gesture1.type in types and gesture2.type in types

    def _should_activate(
        self, gesture1: models.GestureEvent, gesture2: models.GestureEvent
    ) -> bool:
        """Either zoom or rotation thresholds must be met."""
        point1 = gesture1.end_point
        point2 = gesture2.end_point

        distance = geometry.get_distance(point1, point2)
        angle = geometry.get_angle(point1, point2)

        distance_diff = abs(distance - self._start_distance)
        angular_diff = abs(geometry.get_angular_diff(angle, self._start_angle))

        is_zooming = distance_diff >= constants.GestureThreshold.ZOOM_DISTANCE
        is_rotating = angular_diff >= constants.GestureThreshold.ROTATE_ANGLE

        return is_zooming or is_rotating

    def _should_end(
        self, gesture1: models.GestureEvent, gesture2: models.GestureEvent
    ) -> bool:
        """End if one of the gestures is not a hold nor a drag gesture."""
        types = (enums.GestureType.HOLD, enums.GestureType.DRAG)
        return gesture1.type not in types or gesture2.type not in types

    def on_start(
        self, gesture1: models.GestureEvent, gesture2: models.GestureEvent
    ) -> models.GestureEvent:
        """Set the starting values and generate a multi-touch hold gesture."""
        point1 = gesture1.end_point
        point2 = gesture2.end_point

        self._start_distance = geometry.get_distance(point1, point2)
        self._start_angle = geometry.get_angle(point1, point2)

        # Starting distance cannot be 0 when calculating scale factor
        if math.isclose(self._start_distance, 0.0):  # pragma: no cover
            self._start_distance = 0.001

        return models.GestureEvent(
            type=enums.GestureType.MULTI_TOUCH_HOLD,
            start_point=point1,
            end_point=point2,
            mid_point=geometry.get_midpoint(point1, point2),
        )

    def on_update(
        self, gesture1: models.GestureEvent, gesture2: models.GestureEvent
    ) -> models.GestureEvent:
        """Generate a zoom and rotate gesture.

        The gesture has its scaling_factor and rotation_degrees attributes set.
        """
        point1 = gesture1.end_point
        point2 = gesture2.end_point

        distance = geometry.get_distance(point1, point2)
        angle = geometry.get_angle(point1, point2)
        angular_diff = geometry.get_angular_diff(angle, self._start_angle)

        if math.isclose(self._start_distance, 0.0):
            scale = 0.0  # pragma: no cover
        else:
            scale = distance / self._start_distance

        return models.GestureEvent(
            type=enums.GestureType.ZOOM_AND_ROTATE,
            start_point=point1,
            end_point=point2,
            mid_point=geometry.get_midpoint(point1, point2),
            scaling_factor=scale,
            rotation_degrees=angular_diff,
        )

    def on_end(
        self, gesture1: models.GestureEvent, gesture2: models.GestureEvent
    ) -> models.GestureEvent:
        """Generate a multi-touch release gesture."""
        point1 = gesture1.end_point
        point2 = gesture2.end_point

        return models.GestureEvent(
            type=enums.GestureType.MULTI_TOUCH_RELEASE,
            start_point=point1,
            end_point=point2,
            mid_point=geometry.get_midpoint(point1, point2),
        )
