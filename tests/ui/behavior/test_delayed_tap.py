import pytest
import pytest_mock

from pireaderos.common import models
from pireaderos.input import enums
from pireaderos.ui.behavior import delayed_tap


@pytest.fixture
def on_tap(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock and on_hold callback."""
    return mocker.Mock()


def create_delayed_tap_gesture() -> models.GestureEvent:
    """Create a tap gesture."""
    return models.GestureEvent(
        type=enums.GestureType.DELAYED_TAP,
        start_point=models.TouchPoint(0, 0, 0, 0),
        end_point=models.TouchPoint(0, 0, 0, 0),
    )


def create_drag_gesture() -> models.GestureEvent:
    """Create a drag gesture."""
    gesture = create_delayed_tap_gesture()
    gesture.type = enums.GestureType.DRAG
    return gesture


class TestDelayedTapBehaviorInitialization:
    """Test DelayedTapBehavior initialization."""

    def test_init_is_working_unittest(
        self, on_tap: pytest_mock.MockType
    ) -> None:
        """All attributes are present."""
        behavior = delayed_tap.DelayedTapBehavior(on_tap=on_tap)

        assert behavior._on_tap_callback is on_tap


class TestDelayedTapBehaviorHandleGesture:
    """Test DelayedTapBehavior handle_gesture."""

    def test_handle_delayed_tap_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle delayed tap gesture."""
        behavior = delayed_tap.DelayedTapBehavior()
        mock_on_tap = mocker.patch.object(
            behavior, "_on_tap", return_value=None
        )
        gesture = create_delayed_tap_gesture()

        behavior.handle_gesture(gesture)

        mock_on_tap.assert_called_once_with(gesture)

    def test_handle_skips_wrong_gesture_type_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Skip wrong gesture type."""
        behavior = delayed_tap.DelayedTapBehavior()
        mock_on_tap = mocker.patch.object(
            behavior, "_on_tap", return_value=None
        )

        behavior.handle_gesture(create_drag_gesture())

        mock_on_tap.assert_not_called()


class TestDelayedTapBehaviorOnTap:
    """Test DelayedTapBehavior _on_tap."""

    def test_on_tap_calls_callback_unittest(
        self, on_tap: pytest_mock.MockType
    ) -> None:
        """On tap calls callback."""
        behavior = delayed_tap.DelayedTapBehavior(on_tap=on_tap)
        gesture = create_delayed_tap_gesture()

        behavior._on_tap(gesture)

        on_tap.assert_called_once_with(gesture)

    def test_on_tap_skips_none_callback_unittest(self) -> None:
        """On hold skips when callback is None."""
        behavior = delayed_tap.DelayedTapBehavior()

        behavior._on_tap(create_delayed_tap_gesture())  # does not raise error
