# pragma: exclude file
import dataclasses

from pireaderos.common import enums


@dataclasses.dataclass
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


@dataclasses.dataclass
class GestureEvent:
    """The gesture model.

    Attributes:
      type:
        The type of gesture.
      start_point:
        The starting point of the gesture.
      end_point:
        The ending point of the gesture.
      mid_point:
        The middle point of the gesture. Default is None.
      tap_count:
        The number of current taps (single tap, double tap, etc.) Default is 0.
      swipe_direction:
        The direction of the swipe gesture. Default is None.
      scaling_factor:
        The scaling factor change of a zoom and rotate gesture. Default is 1.0.
      rotation_degrees:
        The rotation change of a zoom and rotate gesture in degrees.
        Default is 0.0.

    """

    type: enums.GestureType
    start_point: TouchPoint
    end_point: TouchPoint
    mid_point: TouchPoint | None = None
    tap_count: int = 0
    swipe_direction: enums.SwipeDirection | None = None
    scaling_factor: float = 1.0
    rotation_degrees: float = 0.0


class Percent:
    """Fetch a percentage of the attribute at runtime."""

    def __init__(self, amount: int) -> None:
        self.amount = amount / 100
