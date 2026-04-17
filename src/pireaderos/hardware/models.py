# pragma: exclude file
import dataclasses


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
