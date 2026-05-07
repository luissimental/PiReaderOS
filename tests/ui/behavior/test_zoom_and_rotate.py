import pytest
import pytest_mock

from pireaderos.hardware import models as hw_models
from pireaderos.input import enums, models
from pireaderos.ui.behavior import zoom_and_rotate


@pytest.fixture
def on_zoom_and_rotate(
    mocker: pytest_mock.MockerFixture,
) -> pytest_mock.MockType:
    """Mock an on_zoom_and_rotate callback."""
    return mocker.Mock()


@pytest.fixture
def on_release(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock an on_release callback."""
    return mocker.Mock()


def create_zoom_and_rotate_gesture() -> models.GestureEvent:
    """Create a zoom and rotate gesture."""
    return models.GestureEvent(
        type=enums.GestureType.ZOOM_AND_ROTATE,
        start_point=hw_models.TouchPoint(0, 0, 0, 0),
        end_point=hw_models.TouchPoint(0, 0, 0, 0),
    )


def create_mt_release_gesture() -> models.GestureEvent:
    """Create a multi-touch release gesture."""
    gesture = create_zoom_and_rotate_gesture()
    gesture.type = enums.GestureType.MULTI_TOUCH_RELEASE
    return gesture


class TestZoomAndRotateBehaviorInitialization:
    """Test ZoomAndRotateBehavior initialization."""

    def test_init_is_working_unittest(
        self,
        on_zoom_and_rotate: pytest_mock.MockType,
        on_release: pytest_mock.MockType,
    ) -> None:
        """All attributes are present."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior(
            on_zoom_and_rotate=on_zoom_and_rotate, on_release=on_release
        )

        assert behavior._on_zoom_and_rotate_callback is on_zoom_and_rotate
        assert behavior._on_release_callback is on_release


class TestZoomAndRotateBehaviorHandleGesture:
    """Test ZoomAndRotateBehavior handle_gesture."""

    def test_handle_zoom_and_rotate_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle zoom and rotate gesture."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior()
        mock_on_hold = mocker.patch.object(
            behavior, "_on_zoom_and_rotate", return_value=None
        )
        gesture = create_zoom_and_rotate_gesture()

        behavior.handle_gesture(gesture)

        assert behavior._is_active
        mock_on_hold.assert_called_once_with(gesture)

    def test_handle_release_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle multi-touch release gesture."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior()
        behavior._is_active = True
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )
        gesture = create_mt_release_gesture()

        behavior.handle_gesture(gesture)

        assert not behavior._is_active
        mock_on_release.assert_called_once_with(gesture)

    def test_handle_release_gesture_already_released_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle multi-touch gesture when already released."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior()
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )

        behavior.handle_gesture(create_mt_release_gesture())

        assert not behavior._is_active
        mock_on_release.assert_not_called()


class TestZoomAndRotateBehaviorOnZoomAndRotate:
    """Test ZoomAndRotateBehavior _on_zoom_and_rotate."""

    def test_on_zoom_and_rotate_calls_callback_unittest(
        self, on_zoom_and_rotate: pytest_mock.MockType
    ) -> None:
        """On zoom and rotate calls callback."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior(
            on_zoom_and_rotate=on_zoom_and_rotate
        )
        gesture = create_zoom_and_rotate_gesture()

        behavior._on_zoom_and_rotate(gesture)

        on_zoom_and_rotate.assert_called_once_with(gesture)

    def test_on_zoom_and_rotate_skips_none_callback_unittest(self) -> None:
        """On zoom and rotate skips when callback is None."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior()

        # Does not raise error
        behavior._on_zoom_and_rotate(create_zoom_and_rotate_gesture())


class TestZoomAndRotateBehaviorOnRelease:
    """Test ZoomAndRotateBehavior _on_release."""

    def test_on_release_calls_callback_unittest(
        self, on_release: pytest_mock.MockType
    ) -> None:
        """On release calls callback."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior(on_release=on_release)
        gesture = create_mt_release_gesture()

        behavior._on_release(gesture)

        on_release.assert_called_once_with(gesture)

    def test_on_release_skips_none_callback_unittest(self) -> None:
        """On release skips when callback is None."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior()

        # Does not raise error
        behavior._on_release(create_mt_release_gesture())
