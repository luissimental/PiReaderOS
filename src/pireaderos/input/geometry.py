# pragma: exclude file
import math

from pireaderos.common import models


def get_ordered_points(
    point1: models.TouchPoint, point2: models.TouchPoint
) -> tuple[models.TouchPoint, models.TouchPoint]:
    """Order the points based on their touch_ids.

    Certain operations require the order to be consistent.
    """
    if point1.id < point2.id:
        return point2, point1
    return point1, point2


def get_midpoint(
    point1: models.TouchPoint, point2: models.TouchPoint
) -> models.TouchPoint:
    """Calculate the midpoint between two points.

    Returns:
      A TouchPoint object with its x and y values set to the midpoint
      coordinates. The id and timestamp attributes are set to -1 since the
      coordinates are only relevant.

    """
    mx = (point1.x + point2.x) // 2
    my = (point1.y + point2.y) // 2
    return models.TouchPoint(-1, mx, my, -1)


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


def get_distance(
    point1: models.TouchPoint, point2: models.TouchPoint
) -> float:
    """Calculate the distance between two points."""
    return math.dist((point1.x, point1.y), (point2.x, point2.y))


def get_duration(
    point1: models.TouchPoint, point2: models.TouchPoint
) -> float:
    """Calculate the timestamp difference between two points in seconds."""
    point1, point2 = get_ordered_points(point1, point2)
    return point1.timestamp - point2.timestamp


def get_angle(point1: models.TouchPoint, point2: models.TouchPoint) -> float:
    """Calculate the angle between two points in degrees."""
    dx, dy = get_deltas(point1, point2)
    rad = math.atan2(dy, dx)
    return math.degrees(rad)


def get_angular_diff(current_angle: float, start_angle: float) -> float:
    """Calculate the angular difference between two angles in degrees.

    A positive angular difference is counterclockwise.
    A negative angular difference is clockwise.

    Returns:
      The angular difference in degrees normalized into the range of
      [-180º, 180º).

    """
    return (current_angle - start_angle + 180) % 360 - 180
