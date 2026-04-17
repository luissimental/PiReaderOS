# pragma: exclude file
import math

from pireaderos.input import models


def get_ordered_points(
    point1: models.TouchPoint, point2: models.TouchPoint
) -> tuple[models.TouchPoint, models.TouchPoint]:
    """Order the points based on their touch_ids.

    Certain operations require the order to be consistent.
    """
    if point1.id < point2.id:
        return point2, point1
    return point1, point2


def get_duration(
    point1: models.TouchPoint, point2: models.TouchPoint
) -> float:
    """Calculate the difference between the timestamps."""
    point1, point2 = get_ordered_points(point1, point2)
    return point1.timestamp - point2.timestamp


def get_distance(
    point1: models.TouchPoint, point2: models.TouchPoint
) -> float:
    """Calculate the distance between each point."""
    return math.dist((point1.x, point1.y), (point2.x, point2.y))


def get_deltas(
    point1: models.TouchPoint, point2: models.TouchPoint
) -> tuple[int, int]:
    """Calculate the difference in x and y coordinates between two points.

    Returns:
      A tuple containing (dx, dy).

    """
    point1, point2 = get_ordered_points(point1, point2)
    dx = point1.x - point2.x
    dy = point1.y - point2.y
    return dx, dy
