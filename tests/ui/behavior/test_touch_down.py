import pytest_mock

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import touch_down


@touch_down.behavior_action
def _on_touch_down(
    arg1: component.Component, arg2: models.GestureEvent
) -> None: ...


@touch_down.behavior_action
def _on_release(
    arg1: component.Component, arg2: models.GestureEvent
) -> None: ...


def create_touch_down_gesture() -> models.GestureEvent:
    """Create a touch down gesture."""
    return models.GestureEvent(
        type=enums.GestureType.TOUCH_DOWN,
        start_point=models.TouchPoint(0, 0, 0, 0),
        end_point=models.TouchPoint(0, 0, 0, 0),
    )


def create_release_gesture() -> models.GestureEvent:
    """Create a release gesture."""
    gesture = create_touch_down_gesture()
    gesture.type = enums.GestureType.RELEASE
    return gesture


class TestTouchDownBehaviorInitialization:
    """Test TouchDownBehavior initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        behavior = touch_down.TouchDownBehavior(
            on_touch_down=_on_touch_down, on_release=_on_release
        )

        assert behavior._on_touch_down_callback is _on_touch_down
        assert behavior._on_release_callback is _on_release
        assert not behavior._is_active

    def test_init_argument_signatures_unittest(self) -> None:
        """Behavior accepts callback signatures."""

        @touch_down.behavior_action
        def _on_touch_down2(arg1: component.Component) -> None: ...
        @touch_down.behavior_action
        def _on_release2(arg1: component.Component) -> None: ...

        behavior = touch_down.TouchDownBehavior(
            on_touch_down=_on_touch_down2, on_release=_on_release2
        )

        assert behavior._on_touch_down_callback is _on_touch_down2
        assert behavior._on_release_callback is _on_release2


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
        mock_component = mocker.Mock()
        gesture = create_touch_down_gesture()

        behavior.handle_gesture(mock_component, gesture)

        assert behavior._is_active
        mock_on_touch_down.assert_called_once_with(mock_component, gesture)

    def test_handle_touch_down_gesture_already_active_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle touch down gesture when already active."""
        behavior = touch_down.TouchDownBehavior()
        behavior._is_active = True
        mock_on_touch_down = mocker.patch.object(
            behavior, "_on_touch_down", return_value=None
        )

        behavior.handle_gesture(mocker.Mock(), create_touch_down_gesture())

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
        mock_component = mocker.Mock()
        gesture = create_release_gesture()

        behavior.handle_gesture(mock_component, gesture)

        assert not behavior._is_active
        mock_on_release.assert_called_once_with(mock_component, gesture)

    def test_handle_release_gesture_already_released_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle the release gesture when already released."""
        behavior = touch_down.TouchDownBehavior()
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )

        behavior.handle_gesture(mocker.Mock(), create_release_gesture())

        assert not behavior._is_active
        mock_on_release.assert_not_called()


class TestTouchDownBehaviorSafeCall:
    """Test TouchDownBehavior _safe_call."""

    def test_safe_call_passes_two_args_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Safe call passes owner and gesture to callback."""
        behavior = touch_down.TouchDownBehavior()
        mock_behavior_action = mocker.Mock()
        mock_behavior_action._params_count = 2
        mock_component = mocker.Mock()
        mock_gesture = mocker.Mock()

        behavior._safe_call(mock_behavior_action, mock_component, mock_gesture)

        mock_behavior_action.assert_called_once_with(
            mock_component, mock_gesture
        )

    def test_safe_call_passes_one_arg_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Safe call passes owner to callback."""
        behavior = touch_down.TouchDownBehavior()
        mock_behavior_action = mocker.Mock()
        mock_behavior_action._params_count = 1
        mock_component = mocker.Mock()
        mock_gesture = mocker.Mock()

        behavior._safe_call(mock_behavior_action, mock_component, mock_gesture)

        mock_behavior_action.assert_called_once_with(mock_component)


class TestTouchDownBehaviorOnTouchDown:
    """Test TouchDownBehavior _on_touch_down."""

    def test_on_touch_down_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On touch down calls callback."""
        behavior = touch_down.TouchDownBehavior(on_touch_down=_on_touch_down)
        mock_safe_call = mocker.patch.object(behavior, "_safe_call")
        mock_component = mocker.Mock()
        gesture = create_touch_down_gesture()

        behavior._on_touch_down(mock_component, gesture)

        mock_safe_call.assert_called_once_with(
            _on_touch_down, mock_component, gesture
        )

    def test_on_touch_down_skips_none_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On touch down skips when callback is None."""
        behavior = touch_down.TouchDownBehavior()

        # Does not raise error
        behavior._on_touch_down(mocker.Mock(), create_touch_down_gesture())


class TestTouchDownBehaviorOnRelease:
    """Test TouchDownBehavior _on_release."""

    def test_on_release_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On release calls callback."""
        behavior = touch_down.TouchDownBehavior(on_release=_on_release)
        mock_safe_call = mocker.patch.object(behavior, "_safe_call")
        mock_component = mocker.Mock()
        gesture = create_release_gesture()

        behavior._on_release(mock_component, gesture)

        mock_safe_call.assert_called_once_with(
            _on_release, mock_component, gesture
        )

    def test_on_release_skips_none_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On release skips when callback is None."""
        behavior = touch_down.TouchDownBehavior()

        # Does not raise error
        behavior._on_release(mocker.Mock(), create_release_gesture())
