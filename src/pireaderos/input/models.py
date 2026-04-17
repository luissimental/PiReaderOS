# pragma: exclude file
import dataclasses

from pireaderos.hardware import models
from pireaderos.input import enums


@dataclasses.dataclass
class GestureEvent:
    """The generated gesture.

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
    start_point: models.TouchPoint
    end_point: models.TouchPoint
    mid_point: models.TouchPoint | None = None
    tap_count: int = 0
    swipe_direction: enums.SwipeDirection | None = None
    scaling_factor: float = 1.0
    rotation_degrees: float = 0.0
