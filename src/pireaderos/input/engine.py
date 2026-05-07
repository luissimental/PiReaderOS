from pireaderos.common import models
from pireaderos.input.state_machine import multi_touch, single_touch


class GestureEngine:
    """Central orchestrator for processing raw touch data into gestures.

    Manages finite state machines for single-touch and multi-touch gesture
    recognition. Routes raw touch points through the appropriate state
    machines.

    The engine maintains separate state machines for each touch contact point
    (tracked by ID) and a single multi-touch state machine for two-finger
    gestures. Lifted fingers are detected and processed to generate appropriate
    gestures.

    Example:
      Initialize the engine and process touch data::

        touch_points: list[TouchPoint] = ...
        candidates: list[GestureEvent | None] = []
        engine = GestureEngine()
        candidates = engine.process_touch_points(touch_points)

    """

    def __init__(self) -> None:
        self._single_touch_fsm: dict[
            int, single_touch.SingleTouchStateMachine
        ] = {}
        self._multi_touch_fsm = multi_touch.MultiTouchStateMachine()

    def process_touch_points(
        self, touches: list[models.TouchPoint]
    ) -> list[models.GestureEvent | None]:
        """Process raw touch data and generate gesture candidates.

        Detects lifted fingers and generates release gestures before processing
        active contacts. Routes touch points through appropriate state machines
        based on touch count.

        Args:
          touches:
            A list of touch points. Each point has a unique ID that persists
            across frames for the same physical contact. May be empty when the
            only finger on the screen is lifted.

        Returns:
          A list of candidate gestures for the current frame, which may contain
          None values for gestures not detected yet.

        """
        candidates: list[models.GestureEvent | None] = []

        release_gestures = self._process_lifted_fingers(touches)
        candidates.extend(release_gestures)

        single_touches = self._process_single_touches(touches)
        candidates.extend(single_touches)

        if len(candidates) == 2:
            gest1, gest2 = candidates

            gesture = self._multi_touch_fsm.generate_gesture(gest1, gest2)
            candidates.append(gesture)

        return candidates

    def _process_lifted_fingers(
        self, touches: list[models.TouchPoint]
    ) -> list[models.GestureEvent | None]:
        """Generate release gestures for fingers that have been lifted.

        Compares the set of currently active touches with previously tracked
        touches to detect which fingers have left the screen. For each lifted
        finger, generates a release gesture through its state machine with a
        None input to trigger the release state.

        Args:
          touches:
            List of currently active touch points. Used to identify which
            previously tracked touches are no longer present.

        Returns:
          List of gestures for lifted fingers, or empty list if no fingers have
          been lifted. May contain None values if a state machine does not
          generate a gesture.

        """
        if len(touches) >= len(self._single_touch_fsm):
            return []

        gestures: list[models.GestureEvent | None] = []

        touch_ids = (touch.id for touch in touches)
        present_ids = set(self._single_touch_fsm.keys())
        lifted_ids = present_ids.difference(touch_ids)

        for touch_id in lifted_ids:
            state_machine = self._single_touch_fsm[touch_id]
            gesture = state_machine.generate_gesture(None)
            gestures.append(gesture)

        return gestures

    def _process_single_touches(
        self, touches: list[models.TouchPoint]
    ) -> list[models.GestureEvent | None]:
        """Process touch points individually and generate gestures for each.

        Returns:
          A list of gestures, which may contain None values for gestures not
          detected yet.

        """
        gestures: list[models.GestureEvent | None] = []

        for point in touches:
            # Allocate new state machine if nonexistant
            if point.id not in self._single_touch_fsm:
                self._single_touch_fsm[point.id] = (
                    single_touch.SingleTouchStateMachine()
                )

            state_machine = self._single_touch_fsm[point.id]
            gesture = state_machine.generate_gesture(point)
            gestures.append(gesture)

        return gestures
