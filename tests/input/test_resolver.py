import math
import time

import pytest
import pytest_mock

from pireaderos.common import models
from pireaderos.input import constants, enums, resolver


def gesture_event_as(type_: enums.GestureType) -> models.GestureEvent:
    """Return a GestureEvent as the specified type."""
    return models.GestureEvent(
        type=type_,
        start_point=models.TouchPoint(0, 0, 0, 0),
        end_point=models.TouchPoint(0, 0, 0, 0),
    )


class TestGestureResolverInitialization:
    """Test GestureResolver initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        res = resolver.GestureResolver()

        assert isinstance(res._active_gesture, models.GestureEvent | None)
        assert isinstance(res._timed_gesture, models.GestureEvent | None)
        assert isinstance(res._start_time, float)


class TestGestureResolverProcessTapCandidate:
    """Test GestureResolver _process_tap_candidate."""

    def test_process_sets_tap_as_timed_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Tap count increases and timed gesture is set.

        Old timed gesture is None.
        """
        mocker.patch.object(time, "time", return_value=1.5)
        new_tap = gesture_event_as(enums.GestureType.TAP)

        res = resolver.GestureResolver()
        res._process_tap_candidate(new_tap)

        assert res._timed_gesture is new_tap
        assert res._start_time == 1.5
        assert new_tap.tap_count == 1

    def test_process_stops_when_timed_gesture_is_not_tap_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Tap count increases and timed gesture is set.

        Old timed gesture is not a tap gesture.
        """
        mocker.patch.object(time, "time", return_value=1.5)
        timed_gesture = gesture_event_as(enums.GestureType.HOLD)
        new_tap = gesture_event_as(enums.GestureType.TAP)

        res = resolver.GestureResolver()
        res._timed_gesture = timed_gesture
        res._start_time = 0.5

        res._process_tap_candidate(new_tap)

        assert res._timed_gesture is new_tap
        assert res._start_time == 1.5
        assert new_tap.tap_count == 1

    def test_process_sets_tap_as_timed_but_fails_thresholds_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Tap count only increases by one and timed gesture is set.

        Old timed gesture exists.
        """
        mocker.patch.object(time, "time", return_value=1.5)
        mocker.patch.object(constants.GestureThreshold, "BETWEEN_TAP_TIME", -1)
        mocker.patch.object(
            constants.GestureThreshold, "BETWEEN_TAP_DISTANCE", -1
        )
        timed_gesture = gesture_event_as(enums.GestureType.TAP)
        timed_gesture.tap_count = 1000
        new_tap = gesture_event_as(enums.GestureType.TAP)

        res = resolver.GestureResolver()
        res._timed_gesture = timed_gesture
        res._start_time = 0.5

        res._process_tap_candidate(new_tap)

        assert res._timed_gesture is new_tap
        assert res._start_time == 1.5
        assert new_tap.tap_count == 1

    def test_process_sets_tap_as_timed_and_meets_thresholds_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Tap count increases by the old timed gesture + 1.

        Old timed gesture is replaced by the new tap.
        """
        mocker.patch.object(time, "time", return_value=1.5)
        mocker.patch.object(constants.GestureThreshold, "BETWEEN_TAP_TIME", 10)
        mocker.patch.object(
            constants.GestureThreshold, "BETWEEN_TAP_DISTANCE", 10
        )
        timed_gesture = gesture_event_as(enums.GestureType.TAP)
        timed_gesture.tap_count = 2
        new_tap = gesture_event_as(enums.GestureType.TAP)

        res = resolver.GestureResolver()
        res._timed_gesture = timed_gesture
        res._start_time = 0.5

        res._process_tap_candidate(new_tap)

        assert res._timed_gesture is new_tap
        assert res._start_time == 1.5
        assert new_tap.tap_count == 3


class TestGestureResolverHandleGestureLifecycle:
    """Test GestureResolver _handle_gesture_lifecycle."""

    def test_handle_sets_winner_when_active_gesture_is_none_unittest(
        self,
    ) -> None:
        """Sets winner when active gesture is None."""
        winner = gesture_event_as(enums.GestureType.HOLD)

        res = resolver.GestureResolver()

        gesture: models.GestureEvent | None = None
        gesture = res._handle_gesture_lifecycle(winner)

        assert res._active_gesture is winner
        assert gesture is winner

    @pytest.mark.parametrize(
        "type_",
        [
            type_
            for type_, is_release in constants.GESTURE_IS_RELEASE.items()
            if is_release
        ],
    )
    def test_handle_sets_winner_at_release_unittest(
        self, type_: enums.GestureType
    ) -> None:
        """Sets winner when the active gesture is a release gesture."""
        release = gesture_event_as(type_)
        winner = gesture_event_as(enums.GestureType.HOLD)

        res = resolver.GestureResolver()
        res._active_gesture = release

        gesture: models.GestureEvent | None = None
        gesture = res._handle_gesture_lifecycle(winner)

        assert res._active_gesture is winner
        assert gesture is winner

    @pytest.mark.parametrize(
        "type_",
        [
            type_
            for type_, has_lifecycle in constants.GESTURE_HAS_LIFECYCLE.items()
            if not has_lifecycle
        ],
    )
    def test_handle_sets_winner_when_active_gesture_is_nonlifecycle_unittest(
        self, type_: enums.GestureType
    ) -> None:
        """Sets winner when the active gesture does not have lifecycle."""
        non_lifecycle = gesture_event_as(type_)
        winner = gesture_event_as(enums.GestureType.HOLD)

        res = resolver.GestureResolver()
        res._active_gesture = non_lifecycle

        gesture: models.GestureEvent | None = None
        gesture = res._handle_gesture_lifecycle(winner)

        assert res._active_gesture is winner
        assert gesture is winner

    @pytest.mark.parametrize(
        "winner_type",
        [
            type_
            for type_, is_release in constants.GESTURE_IS_RELEASE.items()
            if not is_release
        ],
    )
    @pytest.mark.parametrize(
        "lifecycle_type",
        [
            type_
            for type_, has_lifecycle in constants.GESTURE_HAS_LIFECYCLE.items()
            if has_lifecycle
        ],
    )
    def test_handle_does_not_set_winner_in_between_lifecycle_unittest(
        self, lifecycle_type: enums.GestureType, winner_type: enums.GestureType
    ) -> None:
        """Does not set winner.

        Winner isn't a release and the active gesture has a lifecycle. This
        represents the middle of a lifecycle which should not reset.
        """
        lifecycle_gesture = gesture_event_as(lifecycle_type)
        winner = gesture_event_as(winner_type)

        res = resolver.GestureResolver()
        res._active_gesture = lifecycle_gesture

        gesture: models.GestureEvent | None = None
        gesture = res._handle_gesture_lifecycle(winner)

        assert res._active_gesture is lifecycle_gesture
        assert gesture is None


class TestGestureResolverShouldSkipDuplicate:
    """Test GestureResolver _should_skip_duplicate."""

    def test_do_not_skip_gestures_with_different_types_unittest(self) -> None:
        """Do not skip gestures with different types."""
        active_gesture = gesture_event_as(enums.GestureType.HOLD)
        winner = gesture_event_as(enums.GestureType.DRAG)

        res = resolver.GestureResolver()
        res._active_gesture = active_gesture

        should_skip: bool = res._should_skip_duplicate(winner)

        assert not should_skip

    def test_skip_duplicate_hold_gesture_unittest(self) -> None:
        """Skip duplicate hold gestures."""
        active_gesture = gesture_event_as(enums.GestureType.HOLD)
        winner = gesture_event_as(enums.GestureType.HOLD)

        res = resolver.GestureResolver()
        res._active_gesture = active_gesture

        should_skip: bool = res._should_skip_duplicate(winner)

        assert should_skip

    def test_skip_duplicate_drag_gesture_unittest(self) -> None:
        """Skip drag gesture when the x and y values match."""
        active_gesture = gesture_event_as(enums.GestureType.DRAG)
        active_gesture.end_point = models.TouchPoint(0, 2, 3, 0)
        winner = gesture_event_as(enums.GestureType.DRAG)
        winner.end_point = models.TouchPoint(0, 2, 3, 0)

        res = resolver.GestureResolver()
        res._active_gesture = active_gesture

        should_skip: bool = res._should_skip_duplicate(winner)

        assert should_skip

    @pytest.mark.parametrize("x2, y2", [(1, 3), (3, 1)])
    @pytest.mark.parametrize("x1, y1", [(1, 2), (2, 1)])
    def test_do_not_skip_updated_drag_gestures_unittest(
        self, x1: int, y1: int, x2: int, y2: int
    ) -> None:
        """Do not skip drag gesture if the x and/or y values are different."""
        active_gesture = gesture_event_as(enums.GestureType.DRAG)
        active_gesture.end_point = models.TouchPoint(0, x1, y1, 0)
        winner = gesture_event_as(enums.GestureType.DRAG)
        winner.end_point = models.TouchPoint(0, x2, y2, 0)

        res = resolver.GestureResolver()
        res._active_gesture = active_gesture

        should_skip: bool = res._should_skip_duplicate(winner)

        assert not should_skip

    def test_skip_duplicated_zoom_and_rotate_gestures_unittest(self) -> None:
        """Skip zoom and rotate gesture.

        Skip when the scales and rotations are the same.
        """
        active_gesture = gesture_event_as(enums.GestureType.ZOOM_AND_ROTATE)
        active_gesture.scaling_factor = math.pi
        active_gesture.rotation_degrees = math.e
        winner = gesture_event_as(enums.GestureType.ZOOM_AND_ROTATE)
        winner.scaling_factor = math.pi
        winner.rotation_degrees = math.e

        res = resolver.GestureResolver()
        res._active_gesture = active_gesture

        should_skip: bool = res._should_skip_duplicate(winner)

        assert should_skip

    @pytest.mark.parametrize(
        "scale2, rotation2", [(math.pi, 0.0), (0.0, math.pi)]
    )
    @pytest.mark.parametrize(
        "scale1, rotation1", [(math.pi, math.e), (math.e, math.pi)]
    )
    def test_do_not_skip_updated_zoom_and_rotate_gestures_unittest(
        self, scale1: float, rotation1: float, scale2: float, rotation2: float
    ) -> None:
        """Do not skip zoom and rotate gesture.

        Do not skip when the scales and/or rotations are different.
        """
        active_gesture = gesture_event_as(enums.GestureType.ZOOM_AND_ROTATE)
        active_gesture.scaling_factor = scale1
        active_gesture.rotation_degrees = rotation1
        winner = gesture_event_as(enums.GestureType.ZOOM_AND_ROTATE)
        winner.scaling_factor = scale2
        winner.rotation_degrees = rotation2

        res = resolver.GestureResolver()
        res._active_gesture = active_gesture

        should_skip: bool = res._should_skip_duplicate(winner)

        assert not should_skip


class TestGestureResolverIsGestureUpdate:
    """Test GestureResolver _is_gesture_update."""

    def test_update_returns_true_if_same_type_unittest(self) -> None:
        """Return True if the winner and active gesture types are the same."""
        active_gesture = gesture_event_as(enums.GestureType.HOLD)
        winner = gesture_event_as(enums.GestureType.HOLD)

        res = resolver.GestureResolver()
        res._active_gesture = active_gesture

        is_update: bool = res._is_gesture_update(winner)

        assert is_update

    @pytest.mark.parametrize(
        "type1, type2",
        [
            (enums.GestureType.HOLD, enums.GestureType.DRAG),
            (enums.GestureType.DRAG, enums.GestureType.HOLD),
        ],
    )
    def test_update_returns_false_if_different_type_unittest(
        self, type1: enums.GestureType, type2: enums.GestureType
    ) -> None:
        """Return False if winner and active gesture types are different."""
        active_gesture = gesture_event_as(type1)
        winner = gesture_event_as(type2)

        res = resolver.GestureResolver()
        res._active_gesture = active_gesture

        is_update: bool = res._is_gesture_update(winner)

        assert not is_update


class TestGestureResolverIsHigherPriority:
    """Test GestureResolver _is_higher_priority."""

    def test_higher_returns_true_when_winner_has_higher_priority_unittest(
        self,
    ) -> None:
        """Return True when winner has higher priority than active gesture."""
        active_gesture = gesture_event_as(enums.GestureType.HOLD)
        winner = gesture_event_as(enums.GestureType.MULTI_TOUCH_RELEASE)

        res = resolver.GestureResolver()
        res._active_gesture = active_gesture

        is_higher_priority: bool = res._is_higher_priority(winner)

        assert is_higher_priority

    def test_higher_returns_false_when_winner_has_lower_priority_unittest(
        self,
    ) -> None:
        """Return False when winner has lower priority than active gesture."""
        active_gesture = gesture_event_as(enums.GestureType.MULTI_TOUCH_HOLD)
        winner = gesture_event_as(enums.GestureType.HOLD)

        res = resolver.GestureResolver()
        res._active_gesture = active_gesture

        is_higher_priority: bool = res._is_higher_priority(winner)

        assert not is_higher_priority


class TestGestureResolverPollTimedGestures:
    """Test GestureResolver poll_timed_gestures."""

    def test_poll_returns_none_when_no_timed_gesture_exists_unittest(
        self,
    ) -> None:
        """Return None when there are no timed gestures to process."""
        res = resolver.GestureResolver()

        gesture: models.GestureEvent | None = None
        gesture = res.poll_timed_gestures()

        assert gesture is None

    def test_poll_returns_none_when_tap_is_not_expired_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return None when the queued tap gesture is still pending."""
        mocker.patch.object(time, "time", return_value=2.5)
        mocker.patch.object(
            constants.GestureThreshold, "BETWEEN_TAP_TIME", 1.6
        )
        timed_gesture = gesture_event_as(enums.GestureType.TAP)

        res = resolver.GestureResolver()
        res._timed_gesture = timed_gesture
        res._start_time = 1.0

        gesture: models.GestureEvent | None = None
        gesture = res.poll_timed_gestures()

        assert res._timed_gesture is timed_gesture
        assert gesture is None

    def test_poll_returns_gesture_when_tap_expires_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return delayed tap when the queued tap expires."""
        mocker.patch.object(time, "time", return_value=2.5)
        mocker.patch.object(
            constants.GestureThreshold, "BETWEEN_TAP_TIME", 1.5
        )
        timed_gesture = gesture_event_as(enums.GestureType.TAP)

        res = resolver.GestureResolver()
        res._timed_gesture = timed_gesture
        res._start_time = 1.0

        gesture: models.GestureEvent | None = None
        gesture = res.poll_timed_gestures()

        assert res._timed_gesture is None
        assert gesture is not None
        assert gesture is timed_gesture
        assert gesture.type is enums.GestureType.DELAYED_TAP


class TestGestureResolverResolvePotentialCandidates:
    """Test GestureResolver resolve_potential_candidates."""

    @pytest.mark.parametrize("candidates", [[], [None], [None, None]])
    def test_resolve_returns_none_on_no_candidates_unittest(
        self, candidates: list[models.GestureEvent | None]
    ) -> None:
        """Return None when candidates is all None or empty."""
        res = resolver.GestureResolver()

        gesture: models.GestureEvent | None = None
        gesture = res.resolve_potential_candidates(candidates)

        assert res._active_gesture is None
        assert gesture is None

    def test_resolve_returns_only_candidate_unittest(self) -> None:
        """Return the only candidate in the list."""
        cand = gesture_event_as(enums.GestureType.HOLD)
        candidates: list[models.GestureEvent | None] = [cand]
        res = resolver.GestureResolver()

        gesture: models.GestureEvent | None = None
        gesture = res.resolve_potential_candidates(candidates)

        assert res._active_gesture is cand
        assert gesture is cand

    def test_resolve_processes_tap_candidate_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return tap gesture and ensure it is processed."""
        process_tap = mocker.patch.object(
            resolver.GestureResolver,
            "_process_tap_candidate",
            return_value=None,
        )
        tap_cand = gesture_event_as(enums.GestureType.TAP)

        gesture: models.GestureEvent | None = None
        res = resolver.GestureResolver()

        gesture = res.resolve_potential_candidates([tap_cand])

        process_tap.assert_called_once_with(tap_cand)
        assert res._active_gesture is tap_cand
        assert gesture is tap_cand

    def test_resolve_returns_beginning_of_lifecycle_unittest(self) -> None:
        """Return the gesture that marks the beginning of lifecycle."""
        hold_cand1 = gesture_event_as(enums.GestureType.HOLD)
        hold_cand2 = gesture_event_as(enums.GestureType.HOLD)
        multi_cand = gesture_event_as(enums.GestureType.MULTI_TOUCH_HOLD)
        candidates: list[models.GestureEvent | None] = [
            hold_cand1,
            hold_cand2,
            multi_cand,
        ]

        gesture: models.GestureEvent | None = None
        res = resolver.GestureResolver()

        gesture = res.resolve_potential_candidates(candidates)

        assert res._active_gesture is multi_cand
        assert gesture is multi_cand

    def test_resolve_returns_middle_of_lifecycle_unittest(self) -> None:
        """Return the gesture that marks the middle of the lifecycle."""
        hold_cand1 = gesture_event_as(enums.GestureType.HOLD)
        hold_cand2 = gesture_event_as(enums.GestureType.HOLD)
        multi_cand = gesture_event_as(enums.GestureType.MULTI_TOUCH_HOLD)
        zoom_and_rotate_cand = gesture_event_as(
            enums.GestureType.ZOOM_AND_ROTATE
        )
        candidates1: list[models.GestureEvent | None] = [
            hold_cand1,
            hold_cand2,
            multi_cand,
        ]
        candidates2: list[models.GestureEvent | None] = [
            hold_cand1,
            hold_cand2,
            zoom_and_rotate_cand,
        ]

        gesture: models.GestureEvent | None = None
        res = resolver.GestureResolver()

        res.resolve_potential_candidates(candidates1)
        gesture = res.resolve_potential_candidates(candidates2)

        assert res._active_gesture is zoom_and_rotate_cand
        assert gesture is zoom_and_rotate_cand

    def test_resolve_returns_end_of_lifecycle_unittest(self) -> None:
        """Return the gesture that marks the end of the lifecycle."""
        hold_cand1 = gesture_event_as(enums.GestureType.HOLD)
        hold_cand2 = gesture_event_as(enums.GestureType.HOLD)
        multi_cand = gesture_event_as(enums.GestureType.MULTI_TOUCH_HOLD)
        release_cand = gesture_event_as(enums.GestureType.RELEASE)
        candidates1: list[models.GestureEvent | None] = [
            hold_cand1,
            hold_cand2,
            multi_cand,
        ]
        candidates2: list[models.GestureEvent | None] = [
            hold_cand1,
            hold_cand2,
            release_cand,
        ]

        gesture: models.GestureEvent | None = None
        res = resolver.GestureResolver()

        res.resolve_potential_candidates(candidates1)
        gesture = res.resolve_potential_candidates(candidates2)

        assert res._active_gesture is release_cand
        assert gesture is release_cand

    def test_resolve_returns_none_on_duplicate_unittest(self) -> None:
        """Return None on duplicate gesture."""
        hold_cand1 = gesture_event_as(enums.GestureType.HOLD)
        hold_cand2 = gesture_event_as(enums.GestureType.HOLD)

        gesture: models.GestureEvent | None = None
        res = resolver.GestureResolver()

        res.resolve_potential_candidates([hold_cand1])
        gesture = res.resolve_potential_candidates([hold_cand2])

        assert res._active_gesture is hold_cand1
        assert gesture is None

    def test_resolve_returns_updated_gesture_unittest(self) -> None:
        """Return gesture with updated attributes."""
        drag_cand1 = gesture_event_as(enums.GestureType.DRAG)
        drag_cand1.end_point = models.TouchPoint(0, 2, 3, 0)
        drag_cand2 = gesture_event_as(enums.GestureType.DRAG)
        drag_cand2.end_point = models.TouchPoint(0, 3, 4, 0)

        gesture: models.GestureEvent | None = None
        res = resolver.GestureResolver()

        res.resolve_potential_candidates([drag_cand1])
        gesture = res.resolve_potential_candidates([drag_cand2])

        assert res._active_gesture is drag_cand2
        assert gesture is drag_cand2

    def test_resolve_returns_higher_priority_gesture_unittest(self) -> None:
        """Return gesture that has a higher priority."""
        hold_cand = gesture_event_as(enums.GestureType.HOLD)
        drag_cand = gesture_event_as(enums.GestureType.DRAG)
        multi_cand = gesture_event_as(enums.GestureType.MULTI_TOUCH_HOLD)

        gesture: models.GestureEvent | None = None
        res = resolver.GestureResolver()

        res.resolve_potential_candidates([hold_cand, drag_cand])
        gesture = res.resolve_potential_candidates([multi_cand])

        assert res._active_gesture is multi_cand
        assert gesture is multi_cand
