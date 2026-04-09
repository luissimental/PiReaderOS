import time
from dataclasses import dataclass
from enum import Enum


class TouchEventType(Enum):
    """Types of touch events that can be detected."""
    DOWN = "down"        # Finger started touching screen
    UP = "up"            # Finger lifted from screen
    CONTACT = "contact"  # Finger remained on screen


@dataclass
class TouchPoint:
    """Represents a single touch point on the screen.

    Attributes:
        id: Unique identifier for the touch contact
        x: X-coordinate of the touch
        y: Y-coordinate of the touch
        timestamp: Time when the touch was recorded (seconds since epoch)
    """
    id: int
    x: int
    y: int
    timestamp: float


@dataclass
class TouchEvent:
    """A detected touch event with its associated touch point data.

    Attributes:
        type: The type of touch event (DOWN, UP, or CONTACT)
        point: The touch point data associated with this event
    """
    type: TouchEventType
    point: TouchPoint


class TouchProcessor:
    """Translates raw touch sensor data into higher-level touch events.

    This processor tracks touch points across frames and detects when fingers
    start touching (DOWN), continue touching (CONTACT), or lift off (UP) the screen.
    It maintains state about which touch IDs are currently active and their
    last known positions.
    """

    def __init__(self):
        self._last_touch: dict[int, TouchPoint | None] = {}
        self._is_touching: dict[int, bool] = {}

    def process_raw_touches(
        self, touches: list[tuple[int, int, int]]
    ) -> list[TouchEvent]:
        """Process raw touch sensor data and generate touch events.

        Args:
            touches: List of (touch_id, x, y) tuples from the touch controller

        Returns:
            List of TouchEvent objects representing detected touch state changes.
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

        Compares the current set of touch IDs with previously tracked IDs
        to find any that are no longer present.

        Args:
            current_touches: Currently active touches from the controller

        Returns:
            List of UP events for lifted fingers
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

        Handles state transitions: initializes new touches, generates DOWN
        events when a finger first touches, and CONTACT events for ongoing
        movement.

        Args:
            touch_id: Unique identifier for this touch
            point: The current touch point data

        Returns:
            List of touch events (DOWN or CONTACT) for this touch point
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
