import pytest
import statemachine

from pireaderos.common import models as hw_models
from pireaderos.input import constants, enums, models
from pireaderos.input.state_machine import single_touch


class TestSingleTouchStateMachineInitialization:
    """Test SingleTouchStateMachine initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        sm = single_touch.SingleTouchStateMachine()

        assert isinstance(sm.idle, statemachine.State)
        assert isinstance(sm.down, statemachine.State)
        assert isinstance(sm.contact, statemachine.State)
        assert isinstance(sm.holding, statemachine.State)
        assert isinstance(sm.dragging, statemachine.State)

        assert isinstance(sm.touch_down, statemachine.event.BoundEvent)
        assert isinstance(sm.touch_contact, statemachine.event.BoundEvent)
        assert isinstance(sm.hold, statemachine.event.BoundEvent)
        assert isinstance(sm.drag, statemachine.event.BoundEvent)
        assert isinstance(sm.release, statemachine.event.BoundEvent)

        assert isinstance(sm._start_point, hw_models.TouchPoint | None)
        assert isinstance(sm._last_point, hw_models.TouchPoint | None)


class TestSingleTouchStateMachineTouchDownEvent:
    """Test SingleTouchStateMachine touch_down."""

    def test_touch_down_transitions_idle_to_down_unittest(self) -> None:
        """Calling event touch_down transitions from idle to down."""
        point = hw_models.TouchPoint(0, 0, 0, 0)
        sm = single_touch.SingleTouchStateMachine()

        gesture: models.GestureEvent | None = sm.touch_down(point)

        assert sm.down in sm.configuration
        assert sm._start_point is point
        assert sm._last_point is point
        assert gesture is not None
        assert gesture.type is enums.GestureType.TOUCH_DOWN
        assert gesture.start_point is point
        assert gesture.end_point is point

    @pytest.mark.parametrize(
        "state",
        [
            single_touch.SingleTouchStateMachine.down,
            single_touch.SingleTouchStateMachine.contact,
            single_touch.SingleTouchStateMachine.holding,
            single_touch.SingleTouchStateMachine.dragging,
        ],
    )
    def test_touch_down_does_not_transition_to_down_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling touch_down doesn't transition from idle to down."""
        point = hw_models.TouchPoint(0, 0, 0, 0)
        sm = single_touch.SingleTouchStateMachine()
        sm.current_state = state

        gesture: models.GestureEvent | None = sm.touch_down(point)

        assert state in sm.configuration
        assert sm._start_point is None
        assert sm._last_point is None
        assert gesture is None


class TestSingleTouchStateMachineTouchContactEvent:
    """Test SingleTouchStateMachine touch_contact."""

    @pytest.mark.parametrize(
        "state",
        [
            single_touch.SingleTouchStateMachine.down,
            single_touch.SingleTouchStateMachine.contact,
        ],
    )
    def test_touch_contact_transitions_to_contact_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling touch_contact transitions from idle to contact."""
        point = hw_models.TouchPoint(0, 0, 0, 0)
        sm = single_touch.SingleTouchStateMachine()
        sm.current_state = state

        sm.touch_contact(point)

        assert sm.contact in sm.configuration
        assert sm._start_point is None
        assert sm._last_point is point

    @pytest.mark.parametrize(
        "state",
        [
            single_touch.SingleTouchStateMachine.idle,
            single_touch.SingleTouchStateMachine.holding,
            single_touch.SingleTouchStateMachine.dragging,
        ],
    )
    def test_touch_contact_does_not_transition_to_contact_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling touch_contact doesn't transition to contact from wrong states."""  # noqa: E501
        point = hw_models.TouchPoint(0, 0, 0, 0)
        sm = single_touch.SingleTouchStateMachine()
        sm.current_state = state

        sm.touch_contact(point)

        assert state in sm.configuration
        assert sm._start_point is None
        assert sm._last_point is None


class TestSingleTouchStateMachineHoldEvent:
    """Test SingleTouchStateMachine hold."""

    @pytest.mark.parametrize(
        "state",
        [
            single_touch.SingleTouchStateMachine.contact,
            single_touch.SingleTouchStateMachine.holding,
        ],
    )
    def test_hold_transitions_to_holding_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling hold transitions to holding."""
        start_point = hw_models.TouchPoint(0, 0, 0, 0)
        point = hw_models.TouchPoint(
            0,
            0,
            constants.GestureThreshold.HOLD_DISTANCE - 1,
            constants.GestureThreshold.HOLD_TIME,
        )

        sm = single_touch.SingleTouchStateMachine()
        sm.current_state = state
        sm._start_point = start_point

        gesture: models.GestureEvent | None = sm.hold(point)

        assert sm.holding in sm.configuration
        assert sm._start_point is start_point
        assert sm._last_point is point
        assert gesture is not None
        assert gesture.type is enums.GestureType.HOLD
        assert gesture.start_point is start_point
        assert gesture.end_point is point

    @pytest.mark.parametrize(
        "state",
        [
            single_touch.SingleTouchStateMachine.contact,
            single_touch.SingleTouchStateMachine.holding,
        ],
    )
    def test_hold_does_not_transition_to_holding_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling hold doesn't transition to holding from wrong states."""
        start_point = hw_models.TouchPoint(0, 0, 0, 0)
        point = hw_models.TouchPoint(0, 0, 0, 0)

        sm = single_touch.SingleTouchStateMachine()
        sm._start_point = start_point
        sm.current_state = state

        gesture: models.GestureEvent | None = sm.hold(point)

        assert state in sm.configuration
        assert sm._start_point is start_point
        assert sm._last_point is None
        assert gesture is None

    @pytest.mark.parametrize(
        "state",
        [
            single_touch.SingleTouchStateMachine.contact,
            single_touch.SingleTouchStateMachine.holding,
        ],
    )
    @pytest.mark.parametrize(
        "point",
        [
            hw_models.TouchPoint(0, 0, 0, 0),  # fails time
            hw_models.TouchPoint(  # fails distance
                0, 0, constants.GestureThreshold.HOLD_DISTANCE, 100000
            ),
        ],
    )
    def test_hold_transition_fails_condition_unittest(
        self, state: statemachine.State, point: hw_models.TouchPoint
    ) -> None:
        """Calling hold fails condition with point."""
        start_point = hw_models.TouchPoint(0, 0, 0, 0)

        sm = single_touch.SingleTouchStateMachine()
        sm.current_state = state
        sm._start_point = start_point

        gesture: models.GestureEvent | None = sm.hold(point)

        assert state in sm.configuration
        assert sm._start_point is start_point
        assert sm._last_point is None
        assert gesture is None


class TestSingleTouchStateMachineDragEvent:
    """Test SingleTouchStateMachine drag."""

    @pytest.mark.parametrize(
        "state",
        [
            single_touch.SingleTouchStateMachine.holding,
            single_touch.SingleTouchStateMachine.dragging,
        ],
    )
    def test_drag_transitions_to_dragging_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling drag transitions to dragging."""
        start_point = hw_models.TouchPoint(0, 0, 0, 0)
        point = hw_models.TouchPoint(
            0, 0, constants.GestureThreshold.DRAG_DISTANCE, 0
        )

        sm = single_touch.SingleTouchStateMachine()
        sm.current_state = state
        sm._start_point = start_point

        gesture: models.GestureEvent | None = sm.drag(point)

        assert sm.dragging in sm.configuration
        assert sm._start_point is start_point
        assert sm._last_point is point
        assert gesture is not None
        assert gesture.type is enums.GestureType.DRAG
        assert gesture.start_point is start_point
        assert gesture.end_point is point

    @pytest.mark.parametrize(
        "state",
        [
            single_touch.SingleTouchStateMachine.idle,
            single_touch.SingleTouchStateMachine.down,
            single_touch.SingleTouchStateMachine.contact,
        ],
    )
    def test_drag_does_not_transition_to_dragging_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling drag doesn't transition to dragging from wrong states."""
        start_point = hw_models.TouchPoint(0, 0, 0, 0)
        point = hw_models.TouchPoint(0, 0, 0, 0)

        sm = single_touch.SingleTouchStateMachine()
        sm._start_point = start_point
        sm.current_state = state

        gesture: models.GestureEvent | None = sm.drag(point)

        assert state in sm.configuration
        assert sm._start_point is start_point
        assert sm._last_point is None
        assert gesture is None

    def test_drag_transition_fails_condition_unittest(self) -> None:
        """Calling drag fails condition with point."""
        start_point = hw_models.TouchPoint(0, 0, 0, 0)
        point = hw_models.TouchPoint(
            0, 0, constants.GestureThreshold.DRAG_DISTANCE - 1, 0
        )

        sm = single_touch.SingleTouchStateMachine()
        sm.current_state = sm.holding
        sm._start_point = start_point

        gesture: models.GestureEvent | None = sm.drag(point)

        assert sm.holding in sm.configuration
        assert sm._start_point is start_point
        assert sm._last_point is None
        assert gesture is None


class TestSingleTouchStateMachineReleaseEvent:
    """Test SingleTouchStateMachine release."""

    @pytest.mark.parametrize(
        "state",
        [
            single_touch.SingleTouchStateMachine.down,
            single_touch.SingleTouchStateMachine.contact,
            single_touch.SingleTouchStateMachine.holding,
            single_touch.SingleTouchStateMachine.dragging,
        ],
    )
    def test_release_transitions_to_idle_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling release transitions to idle."""
        start_point = hw_models.TouchPoint(0, 0, 0, 0)

        sm = single_touch.SingleTouchStateMachine()
        sm._start_point = start_point
        sm.current_state = state

        sm.release()

        assert sm.idle in sm.configuration
        assert sm._start_point is start_point
        assert sm._last_point is None

    def test_release_does_not_transition_to_idle_unittest(self) -> None:
        """Calling release doesn't transition to from idle to idle."""
        start_point = hw_models.TouchPoint(0, 0, 0, 0)

        sm = single_touch.SingleTouchStateMachine()
        sm._start_point = start_point
        sm.current_state = sm.idle

        sm.release()

        assert sm.idle in sm.configuration
        assert sm._start_point is start_point
        assert sm._last_point is None

    @pytest.mark.parametrize(
        "state",
        [
            single_touch.SingleTouchStateMachine.down,
            single_touch.SingleTouchStateMachine.contact,
        ],
    )
    def test_release_returns_tap_gesture_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling release returns tap gesture."""
        start_point = hw_models.TouchPoint(0, 0, 0, 0)
        point = hw_models.TouchPoint(
            0, 0, constants.GestureThreshold.TAP_DISTANCE - 1, 0
        )

        sm = single_touch.SingleTouchStateMachine()
        sm._start_point = start_point
        sm._last_point = point
        sm.current_state = state

        gesture: models.GestureEvent | None = sm.release()

        assert sm.idle in sm.configuration
        assert sm._start_point is start_point
        assert sm._last_point is point
        assert gesture is not None
        assert gesture.type is enums.GestureType.TAP
        assert gesture.start_point is start_point
        assert gesture.end_point is point

    @pytest.mark.parametrize(
        "point, direction",
        [
            (
                hw_models.TouchPoint(
                    0, -constants.GestureThreshold.SWIPE_DISTANCE, 0, 0
                ),
                enums.SwipeDirection.LEFT,
            ),
            (
                hw_models.TouchPoint(
                    0, constants.GestureThreshold.SWIPE_DISTANCE, 0, 0
                ),
                enums.SwipeDirection.RIGHT,
            ),
            (
                hw_models.TouchPoint(
                    0, 0, -constants.GestureThreshold.SWIPE_DISTANCE, 0
                ),
                enums.SwipeDirection.UP,
            ),
            (
                hw_models.TouchPoint(
                    0, 0, constants.GestureThreshold.SWIPE_DISTANCE, 0
                ),
                enums.SwipeDirection.DOWN,
            ),
        ],
    )
    def test_release_returns_swipe_gesture_unittest(
        self,
        point: hw_models.TouchPoint,
        direction: enums.SwipeDirection,
    ) -> None:
        """Calling release returns swipe gesture with direction."""
        start_point = hw_models.TouchPoint(0, 0, 0, 0)

        sm = single_touch.SingleTouchStateMachine()
        sm._start_point = start_point
        sm._last_point = point
        sm.current_state = sm.contact

        gesture: models.GestureEvent | None = sm.release()

        assert sm.idle in sm.configuration
        assert sm._start_point is start_point
        assert sm._last_point is point
        assert gesture is not None
        assert gesture.type is enums.GestureType.SWIPE
        assert gesture.start_point is start_point
        assert gesture.end_point is point
        assert gesture.swipe_direction is direction

    @pytest.mark.parametrize(
        "state",
        [
            single_touch.SingleTouchStateMachine.contact,
            single_touch.SingleTouchStateMachine.holding,
            single_touch.SingleTouchStateMachine.dragging,
        ],
    )
    def test_release_returns_release_gesture_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling release returns release gesture from holding and dragging."""  # noqa: E501
        start_point = hw_models.TouchPoint(0, 0, 0, 0)
        point = hw_models.TouchPoint(0, 100000, 0, 100000)

        sm = single_touch.SingleTouchStateMachine()
        sm._start_point = start_point
        sm._last_point = point
        sm.current_state = state

        gesture: models.GestureEvent | None = sm.release()

        assert sm.idle in sm.configuration
        assert sm._start_point is start_point
        assert sm._last_point is point
        assert gesture is not None
        assert gesture.type is enums.GestureType.RELEASE
        assert gesture.start_point is start_point
        assert gesture.end_point is point


class TestSingleTouchStateMachineGenerateGesture:
    """Test SingleTouchStateMachine generate_gesture."""

    def test_generate_returns_none_on_idle_state_unittest(self) -> None:
        """Return None on idle."""
        sm = single_touch.SingleTouchStateMachine()

        gesture: models.GestureEvent | None = sm.generate_gesture(None)

        assert gesture is None

    def test_generate_returns_touch_down_from_down_state_unittest(
        self,
    ) -> None:
        """Return touch down gesture from down state."""
        down_point = hw_models.TouchPoint(0, 0, 0, 0)

        gesture: models.GestureEvent | None = None
        sm = single_touch.SingleTouchStateMachine()

        gesture = sm.generate_gesture(down_point)
        assert sm.down in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is down_point
        assert gesture is not None
        assert gesture.type is enums.GestureType.TOUCH_DOWN
        assert gesture.start_point is down_point
        assert gesture.end_point is down_point

    def test_generate_returns_none_from_contact_state_unittest(self) -> None:
        """Return None from contact."""
        down_point = hw_models.TouchPoint(0, 0, 0, 0)
        contact_point = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.HOLD_TIME / 2
        )

        gesture: models.GestureEvent | None = None
        sm = single_touch.SingleTouchStateMachine()

        sm.generate_gesture(down_point)

        gesture = sm.generate_gesture(contact_point)
        assert sm.contact in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is contact_point
        assert gesture is None

    def test_generate_returns_hold_gesture_unittest(self) -> None:
        """Return hold gesture."""
        down_point = hw_models.TouchPoint(0, 0, 0, 0)
        contact_point1 = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.HOLD_TIME / 3
        )
        contact_point2 = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.HOLD_TIME / 2
        )
        hold_point1 = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.HOLD_TIME
        )
        hold_point2 = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.HOLD_TIME + 1
        )

        gesture: models.GestureEvent | None = None
        sm = single_touch.SingleTouchStateMachine()

        sm.generate_gesture(down_point)
        sm.generate_gesture(contact_point1)

        gesture = sm.generate_gesture(contact_point2)
        assert sm.contact in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is contact_point2
        assert gesture is None

        gesture = sm.generate_gesture(hold_point1)
        assert sm.holding in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is hold_point1
        assert gesture is not None
        assert gesture.type is enums.GestureType.HOLD
        assert gesture.start_point is down_point
        assert gesture.end_point is hold_point1

        gesture = sm.generate_gesture(hold_point2)
        assert sm.holding in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is hold_point2
        assert gesture is not None
        assert gesture.type is enums.GestureType.HOLD
        assert gesture.start_point is down_point
        assert gesture.end_point is hold_point2

    def test_generate_returns_drag_gesture_unittest(self) -> None:
        """Return drag gesture."""
        down_point = hw_models.TouchPoint(0, 0, 0, 0)
        contact_point = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.HOLD_TIME / 2
        )
        hold_point = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.HOLD_TIME
        )
        drag_point1 = hw_models.TouchPoint(
            0,
            0,
            constants.GestureThreshold.DRAG_DISTANCE,
            constants.GestureThreshold.HOLD_TIME + 1,
        )
        drag_point2 = hw_models.TouchPoint(
            0,
            0,
            constants.GestureThreshold.DRAG_DISTANCE + 100,
            constants.GestureThreshold.HOLD_TIME + 2,
        )

        gesture: models.GestureEvent | None = None
        sm = single_touch.SingleTouchStateMachine()

        sm.generate_gesture(down_point)
        sm.generate_gesture(contact_point)
        sm.generate_gesture(hold_point)

        gesture = sm.generate_gesture(drag_point1)
        assert sm.dragging in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is drag_point1
        assert gesture is not None
        assert gesture.type is enums.GestureType.DRAG
        assert gesture.start_point is down_point
        assert gesture.end_point is drag_point1

        gesture = sm.generate_gesture(drag_point2)
        assert sm.dragging in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is drag_point2
        assert gesture is not None
        assert gesture.type is enums.GestureType.DRAG
        assert gesture.start_point is down_point
        assert gesture.end_point is drag_point2

    def test_generate_returns_tap_gesture_from_down_state_unittest(
        self,
    ) -> None:
        """Return tap gesture from down."""
        down_point = hw_models.TouchPoint(0, 0, 0, 0)

        gesture: models.GestureEvent | None = None
        sm = single_touch.SingleTouchStateMachine()

        sm.generate_gesture(down_point)

        gesture = sm.generate_gesture(None)
        assert sm.idle in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is down_point
        assert gesture is not None
        assert gesture.type is enums.GestureType.TAP
        assert gesture.start_point is down_point
        assert gesture.end_point is down_point

    def test_generate_returns_tap_gesture_from_contact_state_unittest(
        self,
    ) -> None:
        """Return tap gesture from contact."""
        down_point = hw_models.TouchPoint(0, 0, 0, 0)
        contact_point = hw_models.TouchPoint(
            0,
            0,
            constants.GestureThreshold.TAP_DISTANCE - 1,
            constants.GestureThreshold.TAP_TIME / 2,
        )

        gesture: models.GestureEvent | None = None
        sm = single_touch.SingleTouchStateMachine()

        sm.generate_gesture(down_point)
        sm.generate_gesture(contact_point)

        gesture = sm.generate_gesture(None)
        assert sm.idle in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is contact_point
        assert gesture is not None
        assert gesture.type is enums.GestureType.TAP
        assert gesture.start_point is down_point
        assert gesture.end_point is contact_point

    def test_generate_returns_swipe_gesture_unittest(self) -> None:
        """Return swipe gesture."""
        down_point = hw_models.TouchPoint(0, 0, 0, 0)
        contact_point = hw_models.TouchPoint(
            0,
            0,
            constants.GestureThreshold.SWIPE_DISTANCE,
            constants.GestureThreshold.SWIPE_TIME / 2,
        )

        gesture: models.GestureEvent | None = None
        sm = single_touch.SingleTouchStateMachine()

        sm.generate_gesture(down_point)
        sm.generate_gesture(contact_point)

        gesture = sm.generate_gesture(None)
        assert sm.idle in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is contact_point
        assert gesture is not None
        assert gesture.type is enums.GestureType.SWIPE
        assert gesture.start_point is down_point
        assert gesture.end_point is contact_point

    def test_generate_returns_release_gesture_from_contact_state_unittest(
        self,
    ) -> None:
        """Return release gesture from contact."""
        down_point = hw_models.TouchPoint(0, 0, 0, 0)
        contact_point = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.TAP_TIME
        )

        gesture: models.GestureEvent | None = None
        sm = single_touch.SingleTouchStateMachine()

        sm.generate_gesture(down_point)
        sm.generate_gesture(contact_point)

        gesture = sm.generate_gesture(None)
        assert sm.idle in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is contact_point
        assert gesture is not None
        assert gesture.type is enums.GestureType.RELEASE
        assert gesture.start_point is down_point
        assert gesture.end_point is contact_point

    def test_generate_returns_release_gesture_from_holding_state_unittest(
        self,
    ) -> None:
        """Return release gesture from holding."""
        down_point = hw_models.TouchPoint(0, 0, 0, 0)
        contact_point = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.HOLD_TIME / 2
        )
        hold_point = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.HOLD_TIME
        )

        gesture: models.GestureEvent | None = None
        sm = single_touch.SingleTouchStateMachine()

        sm.generate_gesture(down_point)
        sm.generate_gesture(contact_point)
        sm.generate_gesture(hold_point)

        gesture = sm.generate_gesture(None)
        assert sm.idle in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is hold_point
        assert gesture is not None
        assert gesture.type is enums.GestureType.RELEASE
        assert gesture.start_point is down_point
        assert gesture.end_point is hold_point

    def test_generate_returns_release_gesture_from_dragging_state_unittest(
        self,
    ) -> None:
        """Return release gesture from dragging."""
        down_point = hw_models.TouchPoint(0, 0, 0, 0)
        contact_point = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.HOLD_TIME / 2
        )
        hold_point = hw_models.TouchPoint(
            0, 0, 0, constants.GestureThreshold.HOLD_TIME
        )
        drag_point = hw_models.TouchPoint(
            0,
            0,
            constants.GestureThreshold.DRAG_DISTANCE,
            constants.GestureThreshold.HOLD_TIME + 1,
        )

        gesture: models.GestureEvent | None = None
        sm = single_touch.SingleTouchStateMachine()

        sm.generate_gesture(down_point)
        sm.generate_gesture(contact_point)
        sm.generate_gesture(hold_point)
        sm.generate_gesture(drag_point)

        gesture = sm.generate_gesture(None)
        assert sm.idle in sm.configuration
        assert sm._start_point is down_point
        assert sm._last_point is drag_point
        assert gesture is not None
        assert gesture.type is enums.GestureType.RELEASE
        assert gesture.start_point is down_point
        assert gesture.end_point is drag_point
