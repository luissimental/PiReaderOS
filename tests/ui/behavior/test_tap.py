import pytest
import pytest_mock

from pireaderos.common import models as hw_models
from pireaderos.input import enums, models
from pireaderos.ui.behavior import tap


@pytest.fixture
def on_tap(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock an on_hold callback."""
    return mocker.Mock()


def create_tap_gesture() -> models.GestureEvent:
    """Create a tap gesture."""
    return models.GestureEvent(
        type=enums.GestureType.TAP,
        start_point=hw_models.TouchPoint(0, 0, 0, 0),
        end_point=hw_models.TouchPoint(0, 0, 0, 0),
    )


def create_drag_gesture() -> models.GestureEvent:
    """Create a drag gesture."""
    gesture = create_tap_gesture()
    gesture.type = enums.GestureType.DRAG
    return gesture


class TestTapBehaviorInitialization:
    """Test TapBehavior initialization."""

    def test_init_is_working_unittest(
        self, on_tap: pytest_mock.MockType
    ) -> None:
        """All attributes are present."""
        behavior = tap.TapBehavior(on_tap=on_tap)

        assert behavior._on_tap_callback is on_tap


class TestTapBehaviorHandleGesture:
    """Test TapBehavior handle_gesture."""

    def test_handle_tap_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle tap gesture."""
        behavior = tap.TapBehavior()
        mock_on_tap = mocker.patch.object(
            behavior, "_on_tap", return_value=None
        )
        gesture = create_tap_gesture()

        behavior.handle_gesture(gesture)

        mock_on_tap.assert_called_once_with(gesture)

    def test_handle_skips_wrong_gesture_type_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Skip wrong gesture type."""
        behavior = tap.TapBehavior()
        mock_on_tap = mocker.patch.object(
            behavior, "_on_tap", return_value=None
        )

        behavior.handle_gesture(create_drag_gesture())

        mock_on_tap.assert_not_called()


class TestTapBehaviorOnTap:
    """Test TapBehavior _on_tap."""

    def test_on_tap_calls_callback_unittest(
        self, on_tap: pytest_mock.MockType
    ) -> None:
        """On tap calls callback."""
        behavior = tap.TapBehavior(on_tap=on_tap)
        gesture = create_tap_gesture()

        behavior._on_tap(gesture)

        on_tap.assert_called_once_with(gesture)

    def test_on_tap_skips_none_callback_unittest(self) -> None:
        """On hold skips when callback is None."""
        behavior = tap.TapBehavior()

        behavior._on_tap(create_tap_gesture())  # does not raise error
