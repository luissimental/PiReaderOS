from unittest import mock

import pytest_mock

from pireaderos.common import constants, enums, models
from pireaderos.input import engine
from pireaderos.input.state_machine import multi_touch, single_touch


class TestGestureEngineInitialization:
    """Test GestureEngine initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        eng = engine.GestureEngine()

        assert isinstance(eng._single_touch_fsm, dict)
        assert isinstance(
            eng._multi_touch_fsm, multi_touch.MultiTouchStateMachine
        )


class TestGestureEngineProcessLiftedFingers:
    """Test GestureEngine _process_lifted_fingers."""

    def test_process_returns_empty_on_greater_touches_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return empty list when touches is larger than fsm length."""
        touches = [models.TouchPoint(0, 0, 0, 0)]  # lifted touch_id: none
        state_machine = single_touch.SingleTouchStateMachine()
        eng = engine.GestureEngine()
        eng._single_touch_fsm[0] = state_machine

        spy_gen_gest = mocker.patch.object(
            state_machine, "generate_gesture", return_value=None
        )

        gestures: list[models.GestureEvent | None] = []
        gestures = eng._process_lifted_fingers(touches)

        spy_gen_gest.assert_not_called()
        assert len(gestures) == 0

    def test_process_returns_one_lifted_finger_single_touch_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return single lifted finger from a single-touch gesture."""
        touches = []  # lifted touch_id: 0
        state_machine = single_touch.SingleTouchStateMachine()
        eng = engine.GestureEngine()
        eng._single_touch_fsm[0] = state_machine

        spy_gen_gest = mocker.patch.object(
            state_machine, "generate_gesture", return_value=None
        )

        gestures: list[models.GestureEvent | None] = []
        gestures = eng._process_lifted_fingers(touches)

        spy_gen_gest.assert_called_once_with(None)
        assert len(gestures) == 1

    def test_process_returns_one_lifted_finger_multi_touch_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return single lifted finger from a multi-touch gesture."""
        touches = [models.TouchPoint(0, 0, 0, 0)]  # lifted touch_id: 1
        state_machine0 = single_touch.SingleTouchStateMachine()
        state_machine1 = single_touch.SingleTouchStateMachine()
        eng = engine.GestureEngine()
        eng._single_touch_fsm[0] = state_machine0
        eng._single_touch_fsm[1] = state_machine1

        spy_gen_gest0 = mocker.patch.object(
            state_machine0, "generate_gesture", return_value=None
        )
        spy_gen_gest1 = mocker.patch.object(
            state_machine1, "generate_gesture", return_value=None
        )

        gestures: list[models.GestureEvent | None] = []
        gestures = eng._process_lifted_fingers(touches)

        spy_gen_gest0.assert_not_called()
        spy_gen_gest1.assert_called_once_with(None)
        assert len(gestures) == 1

    def test_process_returns_two_lifted_fingers_multi_touch_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return two lifted fingers from a multi-touch gesture."""
        touches = []  # lifted touch_id: 0 and 1
        state_machine0 = single_touch.SingleTouchStateMachine()
        state_machine1 = single_touch.SingleTouchStateMachine()
        eng = engine.GestureEngine()
        eng._single_touch_fsm[0] = state_machine0
        eng._single_touch_fsm[1] = state_machine1

        spy_gen_gest0 = mocker.patch.object(
            state_machine0, "generate_gesture", return_value=None
        )
        spy_gen_gest1 = mocker.patch.object(
            state_machine1, "generate_gesture", return_value=None
        )

        gestures: list[models.GestureEvent | None] = []
        gestures = eng._process_lifted_fingers(touches)

        spy_gen_gest0.assert_called_once_with(None)
        spy_gen_gest1.assert_called_once_with(None)
        assert len(gestures) == 2


class TestGestureEngineProcessSingleTouches:
    """Test GestureEngine _process_single_touches."""

    def test_process_returns_empty_on_empty_touches_unittest(self) -> None:
        """Return empty list when touches is empty."""
        touches = []
        eng = engine.GestureEngine()

        gestures: list[models.GestureEvent | None] = []
        gestures = eng._process_single_touches(touches)

        assert len(eng._single_touch_fsm) == 0
        assert len(gestures) == 0

    def test_process_returns_one_gesture_on_single_touch_exists_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return one gesture on single-touch.

        State machine already exists.
        """
        touches = [models.TouchPoint(0, 0, 0, 0)]
        state_machine = single_touch.SingleTouchStateMachine()
        eng = engine.GestureEngine()
        eng._single_touch_fsm[0] = state_machine

        spy_gen_gest = mocker.patch.object(
            state_machine, "generate_gesture", return_value=None
        )

        gestures: list[models.GestureEvent | None] = []
        gestures = eng._process_single_touches(touches)

        spy_gen_gest.assert_called_once_with(touches[0])
        assert len(gestures) == 1

    def test_process_returns_one_gesture_on_single_touch_nonexistant_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return one gesture on single-touch.

        State machine needs to be allocated.
        """
        mock_state_machine = mocker.patch(
            "pireaderos.input.engine.single_touch.SingleTouchStateMachine"
        )
        touches = [models.TouchPoint(0, 0, 0, 0)]
        eng = engine.GestureEngine()

        gestures: list[models.GestureEvent | None] = []
        gestures = eng._process_single_touches(touches)

        mock_state_machine.assert_called_once()
        mock_state_machine.return_value.generate_gesture.assert_called_once_with(
            touches[0]
        )
        assert len(eng._single_touch_fsm) == 1
        assert len(gestures) == 1

    def test_process_returns_one_gesture_on_multi_touch_existant_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return one gesture on multi-touch.

        State machine already exists.
        """
        touches = [models.TouchPoint(0, 0, 0, 0)]
        state_machine0 = single_touch.SingleTouchStateMachine()
        state_machine1 = single_touch.SingleTouchStateMachine()
        eng = engine.GestureEngine()
        eng._single_touch_fsm[0] = state_machine0
        eng._single_touch_fsm[1] = state_machine1

        spy_gen_gest0 = mocker.patch.object(
            state_machine0, "generate_gesture", return_value=None
        )
        spy_gen_gest1 = mocker.patch.object(
            state_machine1, "generate_gesture", return_value=None
        )

        gestures: list[models.GestureEvent | None] = []
        gestures = eng._process_single_touches(touches)

        spy_gen_gest0.assert_called_once_with(touches[0])
        spy_gen_gest1.assert_not_called()
        assert len(gestures) == 1

    def test_process_returns_one_gesture_on_multi_touch_nonexistant_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return one gesture on multi-touch.

        State machine needs to be allocated.
        """
        touches = [models.TouchPoint(0, 0, 0, 0)]
        state_machine1 = single_touch.SingleTouchStateMachine()
        eng = engine.GestureEngine()
        eng._single_touch_fsm[1] = state_machine1

        spy_gen_gest1 = mocker.patch.object(
            state_machine1, "generate_gesture", return_value=None
        )
        mock_state_machine = mocker.patch(
            "pireaderos.input.engine.single_touch.SingleTouchStateMachine"
        )

        gestures: list[models.GestureEvent | None] = []
        gestures = eng._process_single_touches(touches)

        mock_state_machine.assert_called_once()
        mock_state_machine.return_value.generate_gesture.assert_called_once_with(
            touches[0]
        )
        spy_gen_gest1.assert_not_called()
        assert len(eng._single_touch_fsm) == 2
        assert len(gestures) == 1

    def test_process_returns_two_gestures_on_multi_touch_existant_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return two gestures on multi-touch.

        State machines already exist.
        """
        touches = [
            models.TouchPoint(0, 0, 0, 0),
            models.TouchPoint(1, 0, 0, 0),
        ]
        state_machine0 = single_touch.SingleTouchStateMachine()
        state_machine1 = single_touch.SingleTouchStateMachine()
        eng = engine.GestureEngine()
        eng._single_touch_fsm[0] = state_machine0
        eng._single_touch_fsm[1] = state_machine1

        spy_gen_gest0 = mocker.patch.object(
            state_machine0, "generate_gesture", return_value=None
        )
        spy_gen_gest1 = mocker.patch.object(
            state_machine1, "generate_gesture", return_value=None
        )

        gestures: list[models.GestureEvent | None] = []
        gestures = eng._process_single_touches(touches)

        spy_gen_gest0.assert_called_with(touches[0])
        spy_gen_gest1.assert_called_with(touches[1])
        assert len(gestures) == 2

    def test_process_returns_two_gestures_on_multi_touch_nonexistant_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return two gestures on multi-touch.

        State machines need to be allocated.
        """
        mock_state_machine = mocker.patch(
            "pireaderos.input.engine.single_touch.SingleTouchStateMachine"
        )
        touches = [
            models.TouchPoint(0, 0, 0, 0),
            models.TouchPoint(1, 0, 0, 0),
        ]
        eng = engine.GestureEngine()

        gestures: list[models.GestureEvent | None] = []
        gestures = eng._process_single_touches(touches)

        mock_state_machine.assert_has_calls(
            [
                mock.call(),
                mock.call().generate_gesture(touches[0]),
                mock.call(),
                mock.call().generate_gesture(touches[1]),
            ]
        )
        assert len(eng._single_touch_fsm) == 2
        assert len(gestures) == 2


class TestGestureEngineProcessTouchPoints:
    """Test GestureEngine process_touch_points."""

    def test_generate_returns_empty_on_no_touches_integration(self) -> None:
        """Return empty when there are no touches."""
        touches = []
        eng = engine.GestureEngine()

        gestures: list[models.GestureEvent | None] = []
        gestures = eng.process_touch_points(touches)

        assert len(gestures) == 0

    def test_generate_returns_one_gesture_on_single_touch_integration(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return one gesture on single-touch."""
        mocker.patch.object(constants.GestureThreshold, "HOLD_TIME", 1)
        mocker.patch.object(constants.GestureThreshold, "HOLD_DISTANCE", 1)
        touches1 = [models.TouchPoint(0, 0, 0, 0)]  # down
        touches2 = [models.TouchPoint(0, 0, 0, 0)]  # contact
        touches3 = [models.TouchPoint(0, 0, 0, 1)]  # holding

        gestures: list[models.GestureEvent | None] = []
        eng = engine.GestureEngine()

        eng.process_touch_points(touches1)
        eng.process_touch_points(touches2)
        gestures = eng.process_touch_points(touches3)

        assert len(gestures) == 1
        assert gestures[0] is not None
        assert gestures[0].type is enums.GestureType.HOLD

    def test_generate_returns_release_gesture_on_single_touch_integration(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return release gesture on single-touch."""
        mocker.patch.object(constants.GestureThreshold, "HOLD_TIME", 1)
        mocker.patch.object(constants.GestureThreshold, "HOLD_DISTANCE", 1)
        touches1 = [models.TouchPoint(0, 0, 0, 0)]  # down
        touches2 = [models.TouchPoint(0, 0, 0, 0)]  # contact
        touches3 = [models.TouchPoint(0, 0, 0, 1)]  # holding
        touches4 = []  # release

        gestures: list[models.GestureEvent | None] = []
        eng = engine.GestureEngine()

        eng.process_touch_points(touches1)
        eng.process_touch_points(touches2)
        eng.process_touch_points(touches3)
        gestures = eng.process_touch_points(touches4)

        assert len(gestures) == 1
        assert gestures[0] is not None
        assert gestures[0].type is enums.GestureType.RELEASE

    def test_generate_returns_multi_touch_gesture_integration(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return multi-touch gesture."""
        mocker.patch.object(constants.GestureThreshold, "HOLD_TIME", 1)
        mocker.patch.object(constants.GestureThreshold, "HOLD_DISTANCE", 1)
        touches1 = [  # down
            models.TouchPoint(0, 0, 0, 0),
            models.TouchPoint(1, 0, 0, 0),
        ]
        touches2 = [  # contact
            models.TouchPoint(0, 0, 0, 0),
            models.TouchPoint(1, 0, 0, 0),
        ]
        touches3 = [  # holding
            models.TouchPoint(0, 0, 0, 1),
            models.TouchPoint(1, 0, 0, 1),
        ]

        gestures: list[models.GestureEvent | None] = []
        eng = engine.GestureEngine()

        eng.process_touch_points(touches1)
        eng.process_touch_points(touches2)
        gestures = eng.process_touch_points(touches3)

        assert len(gestures) == 3
        assert gestures[0] is not None
        assert gestures[0].type is enums.GestureType.HOLD
        assert gestures[1] is not None
        assert gestures[1].type is enums.GestureType.HOLD
        assert gestures[2] is not None
        assert gestures[2].type is enums.GestureType.MULTI_TOUCH_HOLD

    def test_generate_returns_release_on_multi_touch_lift_one_integration(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return release when lifting one finger on multi-touch."""
        mocker.patch.object(constants.GestureThreshold, "HOLD_TIME", 1)
        mocker.patch.object(constants.GestureThreshold, "HOLD_DISTANCE", 1)
        touches1 = [  # down
            models.TouchPoint(0, 0, 0, 0),
            models.TouchPoint(1, 0, 0, 0),
        ]
        touches2 = [  # contact
            models.TouchPoint(0, 0, 0, 0),
            models.TouchPoint(1, 0, 0, 0),
        ]
        touches3 = [  # holding
            models.TouchPoint(0, 0, 0, 1),
            models.TouchPoint(1, 0, 0, 1),
        ]
        touches4 = [models.TouchPoint(0, 0, 0, 1)]  # holding, release

        gestures: list[models.GestureEvent | None] = []
        eng = engine.GestureEngine()

        eng.process_touch_points(touches1)
        eng.process_touch_points(touches2)
        eng.process_touch_points(touches3)
        gestures = eng.process_touch_points(touches4)

        assert len(gestures) == 3
        assert gestures[0] is not None
        assert gestures[0].type is enums.GestureType.RELEASE
        assert gestures[1] is not None
        assert gestures[1].type is enums.GestureType.HOLD
        assert gestures[2] is not None
        assert gestures[2].type is enums.GestureType.MULTI_TOUCH_RELEASE

    def test_generate_returns_release_on_multi_touch_lift_two_integration(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return release when lifting two fingers on multi-touch."""
        mocker.patch.object(constants.GestureThreshold, "HOLD_TIME", 1)
        mocker.patch.object(constants.GestureThreshold, "HOLD_DISTANCE", 1)
        touches1 = [  # down
            models.TouchPoint(0, 0, 0, 0),
            models.TouchPoint(1, 0, 0, 0),
        ]
        touches2 = [  # contact
            models.TouchPoint(0, 0, 0, 0),
            models.TouchPoint(1, 0, 0, 0),
        ]
        touches3 = [  # holding
            models.TouchPoint(0, 0, 0, 1),
            models.TouchPoint(1, 0, 0, 1),
        ]
        touches4 = []  # release, release

        gestures: list[models.GestureEvent | None] = []
        eng = engine.GestureEngine()

        eng.process_touch_points(touches1)
        eng.process_touch_points(touches2)
        eng.process_touch_points(touches3)
        gestures = eng.process_touch_points(touches4)

        assert len(gestures) == 3
        assert gestures[0] is not None
        assert gestures[0].type is enums.GestureType.RELEASE
        assert gestures[1] is not None
        assert gestures[1].type is enums.GestureType.RELEASE
        assert gestures[2] is not None
        assert gestures[2].type is enums.GestureType.MULTI_TOUCH_RELEASE
