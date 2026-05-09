import pytest_mock

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import zoom_and_rotate


@zoom_and_rotate.behavior_action
def _on_zoom_and_rotate(
    arg1: component.Component, arg2: models.GestureEvent
) -> None: ...


@zoom_and_rotate.behavior_action
def _on_release(
    arg1: component.Component, arg2: models.GestureEvent
) -> None: ...


def create_zoom_and_rotate_gesture() -> models.GestureEvent:
    """Create a zoom and rotate gesture."""
    return models.GestureEvent(
        type=enums.GestureType.ZOOM_AND_ROTATE,
        start_point=models.TouchPoint(0, 0, 0, 0),
        end_point=models.TouchPoint(0, 0, 0, 0),
    )


def create_mt_release_gesture() -> models.GestureEvent:
    """Create a multi-touch release gesture."""
    gesture = create_zoom_and_rotate_gesture()
    gesture.type = enums.GestureType.MULTI_TOUCH_RELEASE
    return gesture


class TestZoomAndRotateBehaviorInitialization:
    """Test ZoomAndRotateBehavior initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior(
            on_zoom_and_rotate=_on_zoom_and_rotate, on_release=_on_release
        )

        assert behavior._on_zoom_and_rotate_callback is _on_zoom_and_rotate
        assert behavior._on_release_callback is _on_release
        assert not behavior._is_active

    def test_init_argument_signatures_unittest(self) -> None:
        """Behavior accepts callback signatures."""

        @zoom_and_rotate.behavior_action
        def _on_zoom_and_rotate2(arg1: component.Component) -> None: ...
        @zoom_and_rotate.behavior_action
        def _on_release2(arg1: component.Component) -> None: ...

        behavior = zoom_and_rotate.ZoomAndRotateBehavior(
            on_zoom_and_rotate=_on_zoom_and_rotate2, on_release=_on_release2
        )

        assert behavior._on_zoom_and_rotate_callback is _on_zoom_and_rotate2
        assert behavior._on_release_callback is _on_release2


class TestZoomAndRotateBehaviorHandleGesture:
    """Test ZoomAndRotateBehavior handle_gesture."""

    def test_handle_zoom_and_rotate_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle zoom and rotate gesture."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior()
        mock_on_hold = mocker.patch.object(behavior, "_on_zoom_and_rotate")
        mock_component = mocker.Mock()
        gesture = create_zoom_and_rotate_gesture()

        behavior.handle_gesture(mock_component, gesture)

        assert behavior._is_active
        mock_on_hold.assert_called_once_with(mock_component, gesture)

    def test_handle_release_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle multi-touch release gesture."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior()
        behavior._is_active = True
        mock_on_release = mocker.patch.object(behavior, "_on_release")
        mock_component = mocker.Mock()
        gesture = create_mt_release_gesture()

        behavior.handle_gesture(mock_component, gesture)

        assert not behavior._is_active
        mock_on_release.assert_called_once_with(mock_component, gesture)

    def test_handle_release_gesture_already_released_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle multi-touch gesture when already released."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior()
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )

        behavior.handle_gesture(mocker.Mock(), create_mt_release_gesture())

        assert not behavior._is_active
        mock_on_release.assert_not_called()


class TestZoomAndRotateBehaviorOnZoomAndRotate:
    """Test ZoomAndRotateBehavior _on_zoom_and_rotate."""

    def test_on_zoom_and_rotate_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On zoom and rotate calls callback."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior(
            on_zoom_and_rotate=_on_zoom_and_rotate
        )
        mock_safe_call = mocker.patch.object(behavior, "_safe_call")
        mock_component = mocker.Mock()
        gesture = create_zoom_and_rotate_gesture()

        behavior._on_zoom_and_rotate(mock_component, gesture)

        mock_safe_call.assert_called_once_with(
            _on_zoom_and_rotate, mock_component, gesture
        )

    def test_on_zoom_and_rotate_skips_none_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On zoom and rotate skips when callback is None."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior()

        # Does not raise error
        behavior._on_zoom_and_rotate(
            mocker.Mock(), create_zoom_and_rotate_gesture()
        )


class TestZoomAndRotateBehaviorOnRelease:
    """Test ZoomAndRotateBehavior _on_release."""

    def test_on_release_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On release calls callback."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior(
            on_release=_on_release
        )
        mock_safe_call = mocker.patch.object(behavior, "_safe_call")
        mock_component = mocker.Mock()
        gesture = create_mt_release_gesture()

        behavior._on_release(mock_component, gesture)

        mock_safe_call.assert_called_once_with(
            _on_release, mock_component, gesture
        )

    def test_on_release_skips_none_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On release skips when callback is None."""
        behavior = zoom_and_rotate.ZoomAndRotateBehavior()

        # Does not raise error
        behavior._on_release(mocker.Mock(), create_mt_release_gesture())
