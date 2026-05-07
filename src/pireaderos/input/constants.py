# pragma: exclude file
from pireaderos.common import enums


class GestureThreshold:
    """Threshold values for gesture recognition.

    Attributes:
      TAP_TIME:
        in seconds.
      TAP_DISTANCE:
        in pixels.
      BETWEEN_TAP_TIME:
        The time threshold to register subsequent taps in seconds.
      BETWEEN_TAP_DISTANCE:
        The distance threshold to register subsequent taps in pixels.
      HOLD_TIME:
        in seconds.
      HOLD_DISTANCE:
        in pixels.
      DRAG_DISTANCE:
        in pixels.
      SWIPE_TIME:
        in seconds.
      SWIPE_DISTANCE:
        in pixels.
      ZOOM_DISTANCE:
        in pixels.
      ROTATE_ANGLE:
        in degrees.

    """

    # Tap gestures
    TAP_TIME = 0.1  # seconds
    TAP_DISTANCE = 10  # pixels

    # Tap counts (double tap, triple tap, etc.)
    BETWEEN_TAP_TIME = 0.35  # seconds
    BETWEEN_TAP_DISTANCE = 20  # pixels

    # Hold gestures
    HOLD_TIME = 0.25  # seconds
    HOLD_DISTANCE = 10  # pixels

    # Drag gestures
    DRAG_DISTANCE = 10  # pixels

    # Swipe gestures
    SWIPE_TIME = 0.2  # seconds
    SWIPE_DISTANCE = 50  # pixels

    # Zoom and rotate gestures
    ZOOM_DISTANCE = 10  # pixels
    ROTATE_ANGLE = 5  # degrees


# A gesture with a higher priority gets emitted
GESTURE_PRIORITY = {
    enums.GestureType.MULTI_TOUCH_RELEASE: 100,
    enums.GestureType.ZOOM_AND_ROTATE: 90,
    enums.GestureType.MULTI_TOUCH_HOLD: 80,
    enums.GestureType.RELEASE: 70,
    enums.GestureType.DELAYED_TAP: 60,
    enums.GestureType.TAP: 50,
    enums.GestureType.SWIPE: 40,
    enums.GestureType.DRAG: 30,
    enums.GestureType.HOLD: 20,
    enums.GestureType.TOUCH_DOWN: 10,
}

GESTURE_IS_SINGLE_TOUCH = {
    # Single-touch gestures:
    enums.GestureType.RELEASE: True,
    enums.GestureType.DELAYED_TAP: True,
    enums.GestureType.TAP: True,
    enums.GestureType.SWIPE: True,
    enums.GestureType.DRAG: True,
    enums.GestureType.HOLD: True,
    enums.GestureType.TOUCH_DOWN: True,
    # Multi-touch gestures:
    enums.GestureType.MULTI_TOUCH_RELEASE: False,
    enums.GestureType.ZOOM_AND_ROTATE: False,
    enums.GestureType.MULTI_TOUCH_HOLD: False,
}

GESTURE_IS_RELEASE = {
    # Release gestures:
    enums.GestureType.MULTI_TOUCH_RELEASE: True,
    enums.GestureType.RELEASE: True,
    # Non-release gestures:
    enums.GestureType.ZOOM_AND_ROTATE: False,
    enums.GestureType.MULTI_TOUCH_HOLD: False,
    enums.GestureType.DELAYED_TAP: False,
    enums.GestureType.TAP: False,
    enums.GestureType.SWIPE: False,
    enums.GestureType.DRAG: False,
    enums.GestureType.HOLD: False,
    enums.GestureType.TOUCH_DOWN: False,
}

# A gesture has a lifecycle if it triggers a release gesture after it ends
GESTURE_HAS_LIFECYCLE = {
    # Triggers release:
    enums.GestureType.ZOOM_AND_ROTATE: True,
    enums.GestureType.MULTI_TOUCH_HOLD: True,
    enums.GestureType.DRAG: True,
    enums.GestureType.HOLD: True,
    enums.GestureType.TOUCH_DOWN: True,
    # Does not trigger release:
    enums.GestureType.MULTI_TOUCH_RELEASE: False,
    enums.GestureType.RELEASE: False,
    enums.GestureType.DELAYED_TAP: False,
    enums.GestureType.TAP: False,
    enums.GestureType.SWIPE: False,
}
