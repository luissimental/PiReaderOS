import pytest
import pytest_mock

from pireaderos.common import models as hw_models
from pireaderos.input import enums, models
from pireaderos.ui.behavior import swipe


@pytest.fixture
def on_swipe(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock an on_hold_callback."""
    return mocker.Mock()


def create_swipe_gesture() -> models.GestureEvent:
    """Create a swipe gesture."""
    return models.GestureEvent(
        type=enums.GestureType.SWIPE,
        start_point=hw_models.TouchPoint(0, 0, 0, 0),
        end_point=hw_models.TouchPoint(0, 0, 0, 0),
    )


def create_drag_gesture() -> models.GestureEvent:
    """Create a drag gesture."""
    gesture = create_swipe_gesture()
    gesture.type = enums.GestureType.DRAG
    return gesture


class TestSwipeBehaviorInitialization:
    """Test SwipeBehavior initialization."""

    def test_init_is_working_unittest(
        self, on_swipe: pytest_mock.MockType
    ) -> None:
        """All attributes are present."""
        behavior = swipe.SwipeBehavior(on_swipe=on_swipe)

        assert behavior._on_swipe_callback is on_swipe


class TestSwipeBehaviorHandleGesture:
    """Test SwipeBehavior handle_gesture."""

    def test_handle_swipe_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle swipe gesture."""
        behavior = swipe.SwipeBehavior()
        mock_on_swipe = mocker.patch.object(
            behavior, "_on_swipe", return_value=None
        )
        gesture = create_swipe_gesture()

        behavior.handle_gesture(gesture)

        mock_on_swipe.assert_called_once_with(gesture)

    def test_handle_skips_wrong_gesture_type_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Skip wrong gesture type."""
        behavior = swipe.SwipeBehavior()
        mock_on_swipe = mocker.patch.object(
            behavior, "_on_swipe", return_value=None
        )

        behavior.handle_gesture(create_drag_gesture())

        mock_on_swipe.assert_not_called()


class TestSwipeBehaviorOnSwipe:
    """Test SwipeBehavior _on_swipe."""

    def test_on_swipe_calls_callback_unittest(
        self, on_swipe: pytest_mock.MockType
    ) -> None:
        """On swipe calls callback."""
        behavior = swipe.SwipeBehavior(on_swipe=on_swipe)
        gesture = create_swipe_gesture()

        behavior._on_swipe(gesture)

        on_swipe.assert_called_once_with(gesture)

    def test_on_swipe_skips_none_callback_unittest(self) -> None:
        """On swipe skips when callback is None."""
        behavior = swipe.SwipeBehavior()

        behavior._on_swipe(create_swipe_gesture())  # does not raise error
