import pytest
import pytest_mock

from pireaderos.hardware import models as hw_models
from pireaderos.input import enums, models
from pireaderos.ui.behavior import drag


@pytest.fixture
def on_drag(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock an on_drag callback."""
    return mocker.Mock()


@pytest.fixture
def on_release(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock an on_release callback."""
    return mocker.Mock()


def create_drag_gesture() -> models.GestureEvent:
    """Create a drag GestureEvent."""
    return models.GestureEvent(
        type=enums.GestureType.DRAG,
        start_point=hw_models.TouchPoint(0, 0, 0, 0),
        end_point=hw_models.TouchPoint(0, 0, 0, 0),
    )


def create_release_gesture() -> models.GestureEvent:
    """Create a release GestureEvent."""
    gesture = create_drag_gesture()
    gesture.type = enums.GestureType.RELEASE
    return gesture


class TestDragBehaviorInitialization:
    """Test DragBehavior initialization."""

    def test_init_is_working_unittest(
        self, on_drag: pytest_mock.MockType, on_release: pytest_mock.MockType
    ) -> None:
        """All attributes are present."""
        behavior = drag.DragBehavior(on_drag=on_drag, on_release=on_release)

        assert behavior._on_drag_callback is on_drag
        assert behavior._on_release_callback is on_release


class TestDragBehaviorHandleGesture:
    """Test DragBehavior handle_gesture."""

    def test_handle_drag_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle drag gesture."""
        behavior = drag.DragBehavior()
        mock_on_drag = mocker.patch.object(
            behavior, "_on_drag", return_value=None
        )
        gesture = create_drag_gesture()

        behavior.handle_gesture(gesture)

        assert behavior._is_dragging
        mock_on_drag.assert_called_once_with(gesture)

    def test_handle_drag_gesture_already_holding_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle drag gesture when already holding."""
        behavior = drag.DragBehavior()
        behavior._is_dragging = True
        mock_on_drag = mocker.patch.object(
            behavior, "_on_drag", return_value=None
        )
        gesture = create_drag_gesture()

        behavior.handle_gesture(gesture)

        assert behavior._is_dragging
        mock_on_drag.assert_not_called()

    def test_handle_release_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle release gesture."""
        behavior = drag.DragBehavior()
        behavior._is_dragging = True
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )
        gesture = create_release_gesture()

        behavior.handle_gesture(gesture)

        assert not behavior._is_dragging
        mock_on_release.assert_called_once_with(gesture)

    def test_handle_release_gesture_already_released_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle release gesture when already released."""
        behavior = drag.DragBehavior()
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )
        gesture = create_release_gesture()

        behavior.handle_gesture(gesture)

        assert not behavior._is_dragging
        mock_on_release.assert_not_called()


class TestDragBehaviorOnHold:
    """Test DragBehavior _on_hold."""

    def test_on_drag_calls_callback_unittest(
        self, on_drag: pytest_mock.MockType
    ) -> None:
        """On drag calls callback."""
        behavior = drag.DragBehavior(on_drag=on_drag)
        gesture = create_drag_gesture()

        behavior._on_drag(gesture)

        on_drag.assert_called_once_with(gesture)

    def test_on_drag_skips_none_callback_unittest(self) -> None:
        """On drag skips when callback is None."""
        behavior = drag.DragBehavior()

        behavior._on_drag(create_drag_gesture())  # does not raise error


class TestDragBehaviorOnRelease:
    """Test DragBehavior _on_release."""

    def test_on_release_calls_callback_unittest(
        self, on_release: pytest_mock.MockType
    ) -> None:
        """On release calls callback."""
        behavior = drag.DragBehavior(on_release=on_release)
        gesture = create_release_gesture()

        behavior._on_release(gesture)

        on_release.assert_called_once_with(gesture)

    def test_on_release_skips_none_callback_unittest(self) -> None:
        """On release skips when callback is None."""
        behavior = drag.DragBehavior()

        behavior._on_release(create_release_gesture())  # does not raise error
