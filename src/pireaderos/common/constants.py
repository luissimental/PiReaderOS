# pragma: exclude file


class Dimensions:
    """The screen dimensions of the e-paper display."""

    WIDTH = 480
    HEIGHT = 800


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
