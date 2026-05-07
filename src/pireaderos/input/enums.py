# pragma: exclude file
import enum


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
