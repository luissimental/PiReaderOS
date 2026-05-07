import pytest
import pytest_mock

from pireaderos.common import models as hw_models
from pireaderos.input import enums, models
from pireaderos.ui.behavior import touch_down


@pytest.fixture
def on_touch_down(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock an on_touch_down callback."""
    return mocker.Mock()


@pytest.fixture
def on_release(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock an on_release callback."""
    return mocker.Mock()


def create_touch_down_gesture() -> models.GestureEvent:
    """Create a touch down gesture."""
    return models.GestureEvent(
        type=enums.GestureType.TOUCH_DOWN,
        start_point=hw_models.TouchPoint(0, 0, 0, 0),
        end_point=hw_models.TouchPoint(0, 0, 0, 0),
    )


def create_release_gesture() -> models.GestureEvent:
    """Create a release gesture."""
    gesture = create_touch_down_gesture()
    gesture.type = enums.GestureType.RELEASE
    return gesture


class TestTouchDownBehaviorInitialization:
    """Test TouchDownBehavior initialization."""

    def test_init_is_working_unittest(
        self,
        on_touch_down: pytest_mock.MockType,
        on_release: pytest_mock.MockType,
    ) -> None:
        """All attributes are present."""
        behavior = touch_down.TouchDownBehavior(
            on_touch_down=on_touch_down, on_release=on_release
        )

        assert behavior._on_touch_down_callback is on_touch_down
        assert behavior._on_release_callback is on_release
        assert not behavior._is_active


class TestTouchDownBehaviorHandleGesture:
    """Test TouchDownBehavior handle_gesture."""

    def test_handle_touch_down_behavior_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle the touch down gesture."""
        behavior = touch_down.TouchDownBehavior()
        mock_on_touch_down = mocker.patch.object(
            behavior, "_on_touch_down", return_value=None
        )
        gesture = create_touch_down_gesture()

        behavior.handle_gesture(gesture)

        assert behavior._is_active
        mock_on_touch_down.assert_called_once_with(gesture)

    def test_handle_touch_down_gesture_already_active_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle touch down gesture when already active."""
        behavior = touch_down.TouchDownBehavior()
        behavior._is_active = True
        mock_on_touch_down = mocker.patch.object(
            behavior, "_on_touch_down", return_value=None
        )

        behavior.handle_gesture(create_touch_down_gesture())

        assert behavior._is_active
        mock_on_touch_down.assert_not_called()

    def test_handle_release_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle the release gesture."""
        behavior = touch_down.TouchDownBehavior()
        behavior._is_active = True
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )
        gesture = create_release_gesture()

        behavior.handle_gesture(gesture)

        assert not behavior._is_active
        mock_on_release.assert_called_once_with(gesture)

    def test_handle_release_gesture_already_released_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle the release gesture when already released."""
        behavior = touch_down.TouchDownBehavior()
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )

        behavior.handle_gesture(create_release_gesture())

        assert not behavior._is_active
        mock_on_release.assert_not_called()


class TestTouchDownBehaviorOnTouchDown:
    """Test TouchDownBehavior _on_touch_down."""

    def test_on_touch_down_calls_callback_unittest(
        self, on_touch_down: pytest_mock.MockType
    ) -> None:
        """On touch down calls callback."""
        behavior = touch_down.TouchDownBehavior(on_touch_down=on_touch_down)
        gesture = create_touch_down_gesture()

        behavior._on_touch_down(gesture)

        on_touch_down.assert_called_once_with(gesture)

    def test_on_touch_down_skips_none_callback_unittest(self) -> None:
        """On touch down skips when callback is None."""
        behavior = touch_down.TouchDownBehavior()

        # Does not raise error
        behavior._on_touch_down(create_touch_down_gesture())


class TestTouchDownBehaviorOnRelease:
    """Test TouchDownBehavior _on_release."""

    def test_on_release_calls_callback_unittest(
        self, on_release: pytest_mock.MockType
    ) -> None:
        """On release calls callback."""
        behavior = touch_down.TouchDownBehavior(on_release=on_release)
        gesture = create_release_gesture()

        behavior._on_release(gesture)

        on_release.assert_called_once_with(gesture)

    def test_on_release_skips_none_callback_unittest(self) -> None:
        """On release skips when callback is None."""
        behavior = touch_down.TouchDownBehavior()

        # Does not raise error
        behavior._on_release(create_release_gesture())
