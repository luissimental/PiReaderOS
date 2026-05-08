# pragma: exclude file
import enum


class RefreshMode(enum.Enum):
    """The modes to refresh the e-paper display."""

    FULL = enum.auto()
    FAST = enum.auto()
    PARTIAL = enum.auto()


class GestureType(enum.StrEnum):
    """The types of gesture events that can be detected.

    The TAP gesture is an immediate emission for lightweight feedback that can
    be upgraded when the tap count increases. The DELAYED_TAP gesture is a
    delayed emission for more critical actions that cannot be upgraded when
    the tap count increases.
    """

    # Single-touch gestures
    RELEASE = enum.auto()
    TAP = enum.auto()
    DELAYED_TAP = enum.auto()
    HOLD = enum.auto()
    DRAG = enum.auto()
    SWIPE = enum.auto()
    TOUCH_DOWN = enum.auto()

    # Multi-touch gestures
    MULTI_TOUCH_RELEASE = enum.auto()
    MULTI_TOUCH_HOLD = enum.auto()
    ZOOM_AND_ROTATE = enum.auto()


class SwipeDirection(enum.StrEnum):
    """The direction of a swipe gesture."""

    LEFT = enum.auto()
    RIGHT = enum.auto()
    UP = enum.auto()
    DOWN = enum.auto()


# A gesture with a higher priority gets emitted
GESTURE_PRIORITY = {
    GestureType.MULTI_TOUCH_RELEASE: 100,
    GestureType.ZOOM_AND_ROTATE: 90,
    GestureType.MULTI_TOUCH_HOLD: 80,
    GestureType.RELEASE: 70,
    GestureType.DELAYED_TAP: 60,
    GestureType.TAP: 50,
    GestureType.SWIPE: 40,
    GestureType.DRAG: 30,
    GestureType.HOLD: 20,
    GestureType.TOUCH_DOWN: 10,
}

GESTURE_IS_SINGLE_TOUCH = {
    # Single-touch gestures:
    GestureType.RELEASE: True,
    GestureType.DELAYED_TAP: True,
    GestureType.TAP: True,
    GestureType.SWIPE: True,
    GestureType.DRAG: True,
    GestureType.HOLD: True,
    GestureType.TOUCH_DOWN: True,
    # Multi-touch gestures:
    GestureType.MULTI_TOUCH_RELEASE: False,
    GestureType.ZOOM_AND_ROTATE: False,
    GestureType.MULTI_TOUCH_HOLD: False,
}

GESTURE_IS_RELEASE = {
    # Release gestures:
    GestureType.MULTI_TOUCH_RELEASE: True,
    GestureType.RELEASE: True,
    # Non-release gestures:
    GestureType.ZOOM_AND_ROTATE: False,
    GestureType.MULTI_TOUCH_HOLD: False,
    GestureType.DELAYED_TAP: False,
    GestureType.TAP: False,
    GestureType.SWIPE: False,
    GestureType.DRAG: False,
    GestureType.HOLD: False,
    GestureType.TOUCH_DOWN: False,
}

# A gesture has a lifecycle if it triggers a release gesture after it ends
GESTURE_HAS_LIFECYCLE = {
    # Triggers release:
    GestureType.ZOOM_AND_ROTATE: True,
    GestureType.MULTI_TOUCH_HOLD: True,
    GestureType.DRAG: True,
    GestureType.HOLD: True,
    GestureType.TOUCH_DOWN: True,
    # Does not trigger release:
    GestureType.MULTI_TOUCH_RELEASE: False,
    GestureType.RELEASE: False,
    GestureType.DELAYED_TAP: False,
    GestureType.TAP: False,
    GestureType.SWIPE: False,
}
