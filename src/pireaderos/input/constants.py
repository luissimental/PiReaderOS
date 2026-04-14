from dataclasses import dataclass
from enum import Enum


class TouchEventType(Enum):
    """Types of touch events that can be detected."""
    DOWN = "down"  # Finger started touching screen
    UP = "up"  # Finger lifted from screen
    CONTACT = "contact"  # Finger remained on screen


@dataclass
class TouchPoint:
    """A single touch point on the screen.

    Attributes:
      id:
        The unique identifier for the touch contact.
      x:
        The x-coordinate of the touch.
      y:
        The y-coordinate of the touch.
      timestamp:
        The time when the touch was recorded (seconds since epoch).
    """
    id: int
    x: int
    y: int
    timestamp: float


@dataclass
class TouchEvent:
    """A detected touch event with its associated touch point data.

    Attributes:
      type:
        The type of touch event (DOWN, UP, or CONTACT).
      point:
        The touch point data associated with this event.
    """
    type: TouchEventType
    point: TouchPoint
