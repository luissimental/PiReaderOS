import pytest
import pytest_mock

from pireaderos.common import models
from pireaderos.input import enums
from pireaderos.ui.behavior import hold


@pytest.fixture
def on_hold(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock an on_hold callback."""
    return mocker.Mock()


@pytest.fixture
def on_release(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock an on_release callback."""
    return mocker.Mock()


def create_hold_gesture() -> models.GestureEvent:
    """Create a hold GestureEvent."""
    return models.GestureEvent(
        type=enums.GestureType.HOLD,
        start_point=models.TouchPoint(0, 0, 0, 0),
        end_point=models.TouchPoint(0, 0, 0, 0),
    )


def create_release_gesture() -> models.GestureEvent:
    """Create a release GestureEvent."""
    gesture = create_hold_gesture()
    gesture.type = enums.GestureType.RELEASE
    return gesture


class TestHoldBehaviorInitialization:
    """Test HoldBehavior initialization."""

    def test_init_is_working_unittest(
        self, on_hold: pytest_mock.MockType, on_release: pytest_mock.MockType
    ) -> None:
        """All attributes are present."""
        behavior = hold.HoldBehavior(on_hold=on_hold, on_release=on_release)

        assert behavior._on_hold_callback is on_hold
        assert behavior._on_release_callback is on_release


class TestHoldBehaviorHandleGesture:
    """Test HoldBehavior handle_gesture."""

    def test_handle_hold_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle hold gesture."""
        behavior = hold.HoldBehavior()
        mock_on_hold = mocker.patch.object(
            behavior, "_on_hold", return_value=None
        )
        gesture = create_hold_gesture()

        behavior.handle_gesture(gesture)

        assert behavior._is_holding
        mock_on_hold.assert_called_once_with(gesture)

    def test_handle_hold_gesture_already_holding_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle hold gesture when already holding."""
        behavior = hold.HoldBehavior()
        behavior._is_holding = True
        mock_on_hold = mocker.patch.object(
            behavior, "_on_hold", return_value=None
        )
        gesture = create_hold_gesture()

        behavior.handle_gesture(gesture)

        assert behavior._is_holding
        mock_on_hold.assert_not_called()

    def test_handle_release_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle release gesture."""
        behavior = hold.HoldBehavior()
        behavior._is_holding = True
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )
        gesture = create_release_gesture()

        behavior.handle_gesture(gesture)

        assert not behavior._is_holding
        mock_on_release.assert_called_once_with(gesture)

    def test_handle_release_gesture_already_released_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle release gesture when already released."""
        behavior = hold.HoldBehavior()
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )
        gesture = create_release_gesture()

        behavior.handle_gesture(gesture)

        assert not behavior._is_holding
        mock_on_release.assert_not_called()


class TestHoldBehaviorOnHold:
    """Test HoldBehavior _on_hold."""

    def test_on_hold_calls_callback_unittest(
        self, on_hold: pytest_mock.MockType
    ) -> None:
        """On hold calls callback."""
        behavior = hold.HoldBehavior(on_hold=on_hold)
        gesture = create_hold_gesture()

        behavior._on_hold(gesture)

        on_hold.assert_called_once_with(gesture)

    def test_on_hold_skips_none_callback_unittest(self) -> None:
        """On hold skips when callback is None."""
        behavior = hold.HoldBehavior()

        behavior._on_hold(create_hold_gesture())  # does not raise error


class TestHoldBehaviorOnRelease:
    """Test HoldBehavior _on_release."""

    def test_on_release_calls_callback_unittest(
        self, on_release: pytest_mock.MockType
    ) -> None:
        """On release calls callback."""
        behavior = hold.HoldBehavior(on_release=on_release)
        gesture = create_release_gesture()

        behavior._on_release(gesture)

        on_release.assert_called_once_with(gesture)

    def test_on_release_skips_none_callback_unittest(self) -> None:
        """On release skips when callback is None."""
        behavior = hold.HoldBehavior()

        behavior._on_release(create_release_gesture())  # does not raise error
