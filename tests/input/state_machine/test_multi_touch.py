import math

import pytest
import pytest_mock
import statemachine

from pireaderos.common import constants, enums, models
from pireaderos.input.state_machine import multi_touch


class TestMultiTouchStateMachineInitialization:
    """Test MultiTouchStateMachine initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        sm = multi_touch.MultiTouchStateMachine()

        assert isinstance(sm.idle, statemachine.State)
        assert isinstance(sm.two_fingers_down, statemachine.State)
        assert isinstance(sm.transforming, statemachine.State)

        assert isinstance(sm.start, statemachine.event.BoundEvent)
        assert isinstance(sm.activate, statemachine.event.BoundEvent)
        assert isinstance(sm.update, statemachine.event.BoundEvent)
        assert isinstance(sm.end, statemachine.event.BoundEvent)

        assert isinstance(sm._start_distance, float)
        assert isinstance(sm._start_angle, float)


class TestMultiTouchStateMachineStartEvent:
    """Test MultiTouchStateMachine start."""

    @pytest.mark.parametrize(
        "type1, type2",
        [
            (enums.GestureType.HOLD, enums.GestureType.DRAG),
            (enums.GestureType.HOLD, enums.GestureType.HOLD),
            (enums.GestureType.DRAG, enums.GestureType.HOLD),
            (enums.GestureType.DRAG, enums.GestureType.DRAG),
        ],
    )
    def test_start_transitions_to_two_fingers_down_unittest(
        self, type1: enums.GestureType, type2: enums.GestureType
    ) -> None:
        """Calling start transitions to two_fingers_down."""
        gesture1 = models.GestureEvent(
            type=type1,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        gesture2 = models.GestureEvent(
            type=type2,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 4, 0),  # 4 pixels, 90 deg
        )

        sm = multi_touch.MultiTouchStateMachine()

        gesture: models.GestureEvent | None = None
        gesture = sm.start(gesture1, gesture2)

        assert sm.two_fingers_down in sm.configuration
        assert math.isclose(sm._start_distance, 4.0)
        assert math.isclose(sm._start_angle, 90.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.MULTI_TOUCH_HOLD
        assert gesture.start_point is gesture1.end_point
        assert gesture.end_point is gesture2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 2

    @pytest.mark.parametrize(
        "state",
        [
            multi_touch.MultiTouchStateMachine.two_fingers_down,
            multi_touch.MultiTouchStateMachine.transforming,
        ],
    )
    def test_start_does_not_transition_to_two_fingers_down_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling start doesn't transition to two_fingers_down.

        The current state is wrong.
        """
        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 0, 0, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 0, 0, 0),
        )

        sm = multi_touch.MultiTouchStateMachine()
        sm.current_state = state

        gesture: models.GestureEvent | None = None
        gesture = sm.start(start_gest1, start_gest2)

        assert state in sm.configuration
        assert math.isclose(sm._start_distance, 0.0)
        assert math.isclose(sm._start_angle, 0.0)
        assert gesture is None

    @pytest.mark.parametrize(
        "type1, type2",
        [
            (enums.GestureType.HOLD, enums.GestureType.RELEASE),
            (enums.GestureType.DRAG, enums.GestureType.RELEASE),
            (enums.GestureType.RELEASE, enums.GestureType.HOLD),
            (enums.GestureType.RELEASE, enums.GestureType.DRAG),
            (enums.GestureType.RELEASE, enums.GestureType.RELEASE),
        ],
    )
    def test_start_transition_fails_condition_unittest(
        self, type1: enums.GestureType, type2: enums.GestureType
    ) -> None:
        """Calling start fails condition with wrong gesture types."""
        start_gest1 = models.GestureEvent(
            type=type1,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        start_gest2 = models.GestureEvent(
            type=type2,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 0, 2, 0),
        )

        sm = multi_touch.MultiTouchStateMachine()

        gesture: models.GestureEvent | None = None
        gesture = sm.start(start_gest1, start_gest2)

        assert sm.idle in sm.configuration
        assert math.isclose(sm._start_distance, 0.0)
        assert math.isclose(sm._start_angle, 0.0)
        assert gesture is None


class TestMultiTouchStateMachineActivateEvent:
    """Test MultiTouchStateMachine activate."""

    def test_activate_transitions_to_transforming_on_distance_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Calling activate transitions to transforming.

        The event transitions when the zoom distance threshold is met but not
        the rotate angle threshold.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 2)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 1000)

        gesture1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 0, 0, 0),
        )
        gesture2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 4, 0, 0),  # 4 pixels
        )

        sm = multi_touch.MultiTouchStateMachine()
        sm.current_state = sm.two_fingers_down
        sm._start_distance = 2.0
        sm._start_angle = 0.0

        sm.activate(gesture1, gesture2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 2.0)
        assert math.isclose(sm._start_angle, 0.0)

    def test_activate_transitions_to_transforming_on_rotate_angle_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Calling activate transitions to transforming.

        The event transitions when the rotate angle threshold is met but not
        the zoom distance threshold.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 1000)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 45)

        gesture1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        gesture2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 1, 0),  # 90 degrees
        )

        sm = multi_touch.MultiTouchStateMachine()
        sm.current_state = sm.two_fingers_down
        sm._start_distance = 0.0
        sm._start_angle = 45.0

        sm.activate(gesture1, gesture2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 0.0)
        assert math.isclose(sm._start_angle, 45.0)

    def test_activate_transitions_to_transforming_on_true_all_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Calling activate transitions to transforming.

        The event transitions when both the zoom distance and rotate angle
        thresholds are met.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 2)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 45)

        gesture1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        gesture2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 4, 0),  # 4 pixels, 90 deg
        )

        sm = multi_touch.MultiTouchStateMachine()
        sm.current_state = sm.two_fingers_down
        sm._start_distance = 2.0
        sm._start_angle = 45.0

        sm.activate(gesture1, gesture2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 2.0)
        assert math.isclose(sm._start_angle, 45.0)

    @pytest.mark.parametrize(
        "state",
        [
            multi_touch.MultiTouchStateMachine.idle,
            multi_touch.MultiTouchStateMachine.transforming,
        ],
    )
    def test_activate_does_not_transition_to_transforming_unittest(
        self, mocker: pytest_mock.MockerFixture, state: statemachine.State
    ) -> None:
        """Calling activate doesn't transtion to transforming.

        The current state is wrong event though the gestures meet the
        thresholds.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 2)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 45)

        gesture1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        gesture2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 4, 0),  # 4 pixels, 90 deg
        )

        sm = multi_touch.MultiTouchStateMachine()
        sm.current_state = state
        sm._start_distance = 2.0
        sm._start_angle = 45.0

        sm.activate(gesture1, gesture2)

        assert state in sm.configuration
        assert math.isclose(sm._start_distance, 2.0)
        assert math.isclose(sm._start_angle, 45.0)

    def test_activate_fails_condition_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Calling activate fails condition with gestures.

        The gestures do not meet any of the zoom distance or rotate angle
        thresholds.
        """
        # Each threshold is too large by 1
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 3)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 46)

        gesture1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        gesture2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 4, 0),  # 4 pixels, 90 deg
        )

        sm = multi_touch.MultiTouchStateMachine()
        sm.current_state = sm.two_fingers_down
        sm._start_distance = 2.0
        sm._start_angle = 45.0

        sm.activate(gesture1, gesture2)

        assert sm.two_fingers_down in sm.configuration
        assert math.isclose(sm._start_distance, 2.0)
        assert math.isclose(sm._start_angle, 45.0)


class TestMultiTouchStateMachineUpdateEvent:
    """Test MultiTouchStateMachine update."""

    def test_update_returns_zoom_and_rotate_gesture_unittest(self) -> None:
        """Calling update transitions to transforming."""
        gesture1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        gesture2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 4, 0),  # 4 pixels, 90 deg
        )

        sm = multi_touch.MultiTouchStateMachine()
        sm.current_state = sm.transforming
        sm._start_distance = 2.0
        sm._start_angle = 45.0

        gesture: models.GestureEvent | None = None
        gesture = sm.update(gesture1, gesture2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 2.0)
        assert math.isclose(sm._start_angle, 45.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.ZOOM_AND_ROTATE
        assert gesture.start_point is gesture1.end_point
        assert gesture.end_point is gesture2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 2
        assert math.isclose(gesture.scaling_factor, 2.0)
        assert math.isclose(gesture.rotation_degrees, 45.0)

    @pytest.mark.parametrize(
        "state",
        [
            multi_touch.MultiTouchStateMachine.idle,
            multi_touch.MultiTouchStateMachine.two_fingers_down,
        ],
    )
    def test_update_does_not_transition_to_transforming_unittest(
        self, state: statemachine.State
    ) -> None:
        """Calling update doesn't transtion to transforming.

        The current state is wrong.
        """
        gesture1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        gesture2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 4, 0),  # 4 pixels, 90 deg
        )

        sm = multi_touch.MultiTouchStateMachine()
        sm.current_state = state
        sm._start_distance = 2.0
        sm._start_angle = 45.0

        gesture: models.GestureEvent | None = None
        gesture = sm.update(gesture1, gesture2)

        assert state in sm.configuration
        assert math.isclose(sm._start_distance, 2.0)
        assert math.isclose(sm._start_angle, 45.0)
        assert gesture is None


class TestMultiTouchStateMachineEndEvent:
    """Test MultiTouchStateMachine end."""

    @pytest.mark.parametrize(
        "type1, type2",
        [
            (enums.GestureType.HOLD, enums.GestureType.RELEASE),
            (enums.GestureType.DRAG, enums.GestureType.RELEASE),
            (enums.GestureType.RELEASE, enums.GestureType.HOLD),
            (enums.GestureType.RELEASE, enums.GestureType.DRAG),
            (enums.GestureType.RELEASE, enums.GestureType.RELEASE),
        ],
    )
    @pytest.mark.parametrize(
        "state",
        [
            multi_touch.MultiTouchStateMachine.two_fingers_down,
            multi_touch.MultiTouchStateMachine.transforming,
        ],
    )
    def test_end_transitions_to_idle_unittest(
        self,
        state: statemachine.State,
        type1: enums.GestureType,
        type2: enums.GestureType,
    ) -> None:
        """Calling end transitions to idle."""
        gesture1 = models.GestureEvent(
            type=type1,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        gesture2 = models.GestureEvent(
            type=type2,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 4, 0),  # 4 pixels, 90 deg
        )

        sm = multi_touch.MultiTouchStateMachine()
        sm.current_state = state

        gesture: models.GestureEvent | None = None
        gesture = sm.end(gesture1, gesture2)

        assert sm.idle in sm.configuration
        assert gesture is not None
        assert gesture.type is enums.GestureType.MULTI_TOUCH_RELEASE
        assert gesture.start_point is gesture1.end_point
        assert gesture.end_point is gesture2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 2

    def test_end_does_not_transition_to_idle_unittest(self) -> None:
        """Calling end doesn't transition to idle on wrong state."""
        gesture1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        gesture2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 4, 0),  # 4 pixels, 90 deg
        )

        sm = multi_touch.MultiTouchStateMachine()
        sm.current_state = sm.idle

        gesture: models.GestureEvent | None = None
        gesture = sm.end(gesture1, gesture2)

        assert sm.idle in sm.configuration
        assert gesture is None


class TestMultiTouchStateMachineGenerateGesture:
    """Test MultiTouchStateMachine generate_gesture."""

    def test_generate_returns_none_if_input_is_none_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return None if a gesture is None."""
        sm = multi_touch.MultiTouchStateMachine()

        gesture: models.GestureEvent | None = None

        gesture = sm.generate_gesture(mocker.Mock(), None)
        assert sm.idle in sm.configuration
        assert math.isclose(sm._start_distance, 0.0)
        assert math.isclose(sm._start_angle, 0.0)
        assert gesture is None

        gesture = sm.generate_gesture(None, mocker.Mock())
        assert sm.idle in sm.configuration
        assert math.isclose(sm._start_distance, 0.0)
        assert math.isclose(sm._start_angle, 0.0)
        assert gesture is None

        gesture = sm.generate_gesture(None, None)
        assert sm.idle in sm.configuration
        assert math.isclose(sm._start_distance, 0.0)
        assert math.isclose(sm._start_angle, 0.0)
        assert gesture is None

    @pytest.mark.parametrize(
        "type1, type2",
        [
            (enums.GestureType.HOLD, enums.GestureType.RELEASE),
            (enums.GestureType.DRAG, enums.GestureType.RELEASE),
            (enums.GestureType.RELEASE, enums.GestureType.HOLD),
            (enums.GestureType.RELEASE, enums.GestureType.DRAG),
            (enums.GestureType.RELEASE, enums.GestureType.RELEASE),
        ],
    )
    def test_generate_returns_none_if_start_fails_condition_unittest(
        self, type1: enums.GestureType, type2: enums.GestureType
    ) -> None:
        """Return None if start fails condition."""
        start_gest1 = models.GestureEvent(
            type=type1,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        start_gest2 = models.GestureEvent(
            type=type2,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 0, 2, 0),
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        gesture = sm.generate_gesture(start_gest1, start_gest2)

        assert sm.idle in sm.configuration
        assert math.isclose(sm._start_distance, 0.0)
        assert math.isclose(sm._start_angle, 0.0)
        assert gesture is None

    def test_generate_returns_multi_touch_hold_from_idle_state_unittest(
        self,
    ) -> None:
        """Return multi-touch hold gesture."""
        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 4, 0),  # 4 pixels, 90 deg
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        gesture = sm.generate_gesture(start_gest1, start_gest2)

        assert sm.two_fingers_down in sm.configuration
        assert math.isclose(sm._start_distance, 4.0)
        assert math.isclose(sm._start_angle, 90.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.MULTI_TOUCH_HOLD
        assert gesture.start_point is start_gest1.end_point
        assert gesture.end_point is start_gest2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 2

    def test_generate_returns_none_if_activate_fails_condition_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return None if activate fails condition."""
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 1000)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 1000)
        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 4, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 0, 0),  # 4 pixels, -90 deg
        )
        activate_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 2, 0),
        )
        activate_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 0, 0),  # 2 pixels, -90 deg
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(activate_gest1, activate_gest2)

        assert sm.two_fingers_down in sm.configuration
        assert math.isclose(sm._start_distance, 4.0)
        assert math.isclose(sm._start_angle, -90.0)
        assert gesture is None

    def test_generate_returns_zoom_and_rotate_up_to_down_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return zoom and rotate gesture.

        One finger moves from up to down as a zoom in.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 4, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 0, 0),  # 4 pixels, -90 deg
        )
        update_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 2, 0),
        )
        update_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 0, 0),  # 2 pixels, -90 deg
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(update_gest1, update_gest2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 4.0)
        assert math.isclose(sm._start_angle, -90.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.ZOOM_AND_ROTATE
        assert gesture.start_point is update_gest1.end_point
        assert gesture.end_point is update_gest2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 1
        assert math.isclose(gesture.scaling_factor, 0.5)
        assert math.isclose(gesture.rotation_degrees, 0.0)

    def test_generate_returns_zoom_and_rotate_down_to_up_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return zoom and rotate gesture.

        One finger moves from down to up as a zoom in.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 4, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 0, 0),  # 4 pixels, -90 deg
        )
        update_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 4, 0),
        )
        update_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 2, 0),  # 2 pixels, -90 deg
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(update_gest1, update_gest2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 4.0)
        assert math.isclose(sm._start_angle, -90.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.ZOOM_AND_ROTATE
        assert gesture.start_point is update_gest1.end_point
        assert gesture.end_point is update_gest2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 3
        assert math.isclose(gesture.scaling_factor, 0.5)
        assert math.isclose(gesture.rotation_degrees, 0.0)

    def test_generate_returns_zoom_and_rotate_left_to_right_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return zoom and rotate gesture.

        One finger moves from left to right as a zoom in.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 0, 1, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 4, 1, 0),  # 4 pixels, 0 deg
        )
        update_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 2, 1, 0),
        )
        update_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 4, 1, 0),  # 2 pixels, 0 deg
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(update_gest1, update_gest2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 4.0)
        assert math.isclose(sm._start_angle, 0.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.ZOOM_AND_ROTATE
        assert gesture.start_point is update_gest1.end_point
        assert gesture.end_point is update_gest2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 3
        assert gesture.mid_point.y == 1
        assert math.isclose(gesture.scaling_factor, 0.5)
        assert math.isclose(gesture.rotation_degrees, 0.0)

    def test_generate_returns_zoom_and_rotate_right_to_left_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return zoom and rotate gesture.

        One finger moves from right to left as a zoom in.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 0, 1, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 4, 1, 0),  # 4 pixels, 0 deg
        )
        update_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 0, 1, 0),
        )
        update_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 2, 1, 0),  # 2 pixels, 0 deg
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(update_gest1, update_gest2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 4.0)
        assert math.isclose(sm._start_angle, 0.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.ZOOM_AND_ROTATE
        assert gesture.start_point is update_gest1.end_point
        assert gesture.end_point is update_gest2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 1
        assert math.isclose(gesture.scaling_factor, 0.5)
        assert math.isclose(gesture.rotation_degrees, 0.0)

    def test_generate_returns_zoom_and_rotate_both_move_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return zoom and rotate gesture.

        Both fingers move from left to right as a drag.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 4, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 0, 0),  # 4 pixels, -90 deg
        )
        update_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 3, 4, 0),
        )
        update_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 3, 0, 0),  # 4 pixels, -90 deg
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(update_gest1, update_gest2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 4.0)
        assert math.isclose(sm._start_angle, -90.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.ZOOM_AND_ROTATE
        assert gesture.start_point is update_gest1.end_point
        assert gesture.end_point is update_gest2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 3
        assert gesture.mid_point.y == 2
        assert math.isclose(gesture.scaling_factor, 1.0)
        assert math.isclose(gesture.rotation_degrees, 0.0)

    def test_generate_returns_zoom_and_rotate_both_move_out_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return zoom and rotate gesture.

        Both fingers move in opposite directions as a zoom out.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 4, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 2, 0),  # 2 pixels, -90 deg
        )
        update_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 8, 0),
        )
        update_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 0, 0),  # 8 pixels, -90 deg
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(update_gest1, update_gest2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 2.0)
        assert math.isclose(sm._start_angle, -90.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.ZOOM_AND_ROTATE
        assert gesture.start_point is update_gest1.end_point
        assert gesture.end_point is update_gest2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 4
        assert math.isclose(gesture.scaling_factor, 4.0)
        assert math.isclose(gesture.rotation_degrees, 0.0)

    def test_generate_returns_zoom_and_rotate_counterclockwise_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return zoom and rotate gesture.

        One finger rotates counterclockwise.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 2, 1, 0),  # 4 pixels, 45 deg
        )
        update_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        update_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, 1, 0),  # 1 pixel, 90 deg
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(update_gest1, update_gest2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, math.sqrt(2))
        assert math.isclose(sm._start_angle, 45.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.ZOOM_AND_ROTATE
        assert gesture.start_point is update_gest1.end_point
        assert gesture.end_point is update_gest2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 0
        assert math.isclose(gesture.scaling_factor, 1 / math.sqrt(2))
        assert math.isclose(gesture.rotation_degrees, 45.0)

    def test_generate_returns_zoom_and_rotate_clockwise_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return zoom and rotate gesture.

        One finger rotates clockwise.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 2, 1, 0),  # sqrt2 pixels, 45 deg
        )
        update_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 0, 0),
        )
        update_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 2, 0, 0),  # 2 pixels, 0 deg
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(update_gest1, update_gest2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, math.sqrt(2))
        assert math.isclose(sm._start_angle, 45.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.ZOOM_AND_ROTATE
        assert gesture.start_point is update_gest1.end_point
        assert gesture.end_point is update_gest2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 0
        assert math.isclose(gesture.scaling_factor, 1 / math.sqrt(2))
        assert math.isclose(gesture.rotation_degrees, -45.0)

    def test_generate_returns_zoom_and_rotate_counterclockwise_both_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return zoom and rotate gesture.

        Both fingers rotate counterclockwise.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 1, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, -1, 0),  # 2 pixels, -90 deg
        )
        update_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 0, 1, 0),
        )
        update_gest2 = models.GestureEvent(  # 2sqrt2 pixels, -45 deg
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 2, -1, 0),
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(update_gest1, update_gest2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 2.0)
        assert math.isclose(sm._start_angle, -90.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.ZOOM_AND_ROTATE
        assert gesture.start_point is update_gest1.end_point
        assert gesture.end_point is update_gest2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 0
        assert math.isclose(gesture.scaling_factor, math.sqrt(2))
        assert math.isclose(gesture.rotation_degrees, 45.0)

    def test_generate_returns_zoom_and_rotate_clockwise_both_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return zoom and rotate gesture.

        Both fingers rotate clockwise.
        """
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 1, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, -1, 0),  # 2 pixels, -90 deg
        )
        update_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 2, 1, 0),
        )
        update_gest2 = models.GestureEvent(  # 2sqrt2 pixels, -135 deg
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 0, -1, 0),
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(update_gest1, update_gest2)

        assert sm.transforming in sm.configuration
        assert math.isclose(sm._start_distance, 2.0)
        assert math.isclose(sm._start_angle, -90.0)
        assert gesture is not None
        assert gesture.type is enums.GestureType.ZOOM_AND_ROTATE
        assert gesture.start_point is update_gest1.end_point
        assert gesture.end_point is update_gest2.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 0
        assert math.isclose(gesture.scaling_factor, math.sqrt(2))
        assert math.isclose(gesture.rotation_degrees, -45.0)

    def test_generate_returns_release_on_transforming_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Returns multi-touch release on transforming state."""
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 1, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, -1, 0),  # 2 pixels, -90 deg
        )
        update_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 2, 1, 0),
        )
        update_gest2 = models.GestureEvent(  # 2sqrt2 pixels, -135 deg
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 0, -1, 0),
        )
        release_gest = models.GestureEvent(
            type=enums.GestureType.RELEASE,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 0, -1, 0),
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        sm.generate_gesture(update_gest1, update_gest2)
        gesture = sm.generate_gesture(update_gest1, release_gest)

        assert sm.idle in sm.configuration
        assert gesture is not None
        assert gesture.type is enums.GestureType.MULTI_TOUCH_RELEASE
        assert gesture.start_point is update_gest1.end_point
        assert gesture.end_point is release_gest.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 1
        assert gesture.mid_point.y == 0

    def test_generate_returns_release_on_two_fingers_down_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Returns multi-touch release on two_fingers_down state."""
        mocker.patch.object(constants.GestureThreshold, "ZOOM_DISTANCE", 0)
        mocker.patch.object(constants.GestureThreshold, "ROTATE_ANGLE", 0)

        start_gest1 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(0, 0, 0, 0),
            end_point=models.TouchPoint(0, 1, 1, 0),
        )
        start_gest2 = models.GestureEvent(
            type=enums.GestureType.HOLD,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 1, -1, 0),  # 2 pixels, -90 deg
        )
        release_gest = models.GestureEvent(
            type=enums.GestureType.RELEASE,
            start_point=models.TouchPoint(1, 0, 0, 0),
            end_point=models.TouchPoint(1, 0, -1, 0),
        )

        gesture: models.GestureEvent | None = None
        sm = multi_touch.MultiTouchStateMachine()

        sm.generate_gesture(start_gest1, start_gest2)
        gesture = sm.generate_gesture(start_gest1, release_gest)

        assert sm.idle in sm.configuration
        assert gesture is not None
        assert gesture.type is enums.GestureType.MULTI_TOUCH_RELEASE
        assert gesture.start_point is start_gest1.end_point
        assert gesture.end_point is release_gest.end_point
        assert gesture.mid_point is not None
        assert gesture.mid_point.x == 0
        assert gesture.mid_point.y == 0
