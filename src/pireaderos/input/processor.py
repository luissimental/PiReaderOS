import time

from pireaderos.input.constants import TouchEvent, TouchEventType, TouchPoint


class TouchProcessor:
    """Translate raw touch sensor data into higher-level touch events.

    Track touch points across frames and detects when fingers start touching
    (DOWN), continue touching (CONTACT), or lift off (UP) thescreen. It
    maintains state about which touch IDs are currently active and their last
    known positions.
    """

    def __init__(self):
        self._last_touch: dict[int, TouchPoint | None] = {}
        self._is_touching: dict[int, bool] = {}

    def process_raw_touches(
        self, touches: list[tuple[int, int, int]]
    ) -> list[TouchEvent]:
        """Process raw touch sensor data and generate touch events.

        Args:
          touches:
            A list of (touch_id, x, y) tuples from the touch controller.

        Returns:
          A list of TouchEvent objects representing detected touch state
          changes.
        """
        now = time.time()
        events = []

        # Detect fingers that have been lifted from the screen
        events.extend(self._process_lifted_fingers(touches))

        # Process touches currently on the screen
        for touch in touches:
            pid, x, y = touch
            point = TouchPoint(pid, x, y, now)
            events.extend(self._process_touch_point(pid, point))

        return events

    def _process_lifted_fingers(
        self, current_touches: list[tuple[int, int, int]]
    ) -> list[TouchEvent]:
        """Detect and generate events for fingers that have been lifted.

        Compare the current set of touch IDs with previously tracked IDs
        to find any that are no longer present.

        Args:
          current_touches:
            The active touches from the controller.

        Returns:
          A list of UP touch events for lifted fingers.
        """
        events = []

        # Only process if we have more tracked touches than current touches
        if len(self._last_touch) <= len(current_touches):
            return events

        current_touch_ids = {touch[0] for touch in current_touches}
        lifted_touch_ids = set(self._last_touch.keys()) - current_touch_ids

        for touch_id in lifted_touch_ids:
            point = self._last_touch.pop(touch_id)
            was_touching = self._is_touching.pop(touch_id)

            # Only generate UP event if the finger was actually touching
            if point and was_touching:
                events.append(TouchEvent(TouchEventType.UP, point))

        return events

    def _process_touch_point(
        self, touch_id: int, point: TouchPoint
    ) -> list[TouchEvent]:
        """Process a single touch point and generate appropriate events.

        Handle state transitions: initialize new touches, generate DOWN
        events when a finger first touches, and CONTACT events for ongoing
        movement.

        Args:
          touch_id: The unique identifier for this touch.
          point: The current touch point data.

        Returns:
          A list of touch events (DOWN or CONTACT) for this touch point.
        """
        events = []

        # Initialize state for new touch IDs
        if touch_id not in self._is_touching:
            self._is_touching[touch_id] = False
            self._last_touch[touch_id] = None

        # Check if finger was already touching (generating CONTACT event)
        if self._is_touching[touch_id]:
            self._last_touch[touch_id] = point
            events.append(TouchEvent(TouchEventType.CONTACT, point))
        # Finger is starting to touch (generating DOWN event)
        else:
            self._is_touching[touch_id] = True
            self._last_touch[touch_id] = point
            events.append(TouchEvent(TouchEventType.DOWN, point))

        return events
