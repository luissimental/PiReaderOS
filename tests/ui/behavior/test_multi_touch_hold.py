import pytest_mock

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import multi_touch_hold


@multi_touch_hold.behavior_action
def _on_hold(arg1: component.Component, arg2: models.GestureEvent) -> None: ...


@multi_touch_hold.behavior_action
def _on_release(
    arg1: component.Component, arg2: models.GestureEvent
) -> None: ...


def create_mt_hold_gesture() -> models.GestureEvent:
    """Create a multi-touch hold gesture."""
    return models.GestureEvent(
        type=enums.GestureType.MULTI_TOUCH_HOLD,
        start_point=models.TouchPoint(0, 0, 0, 0),
        end_point=models.TouchPoint(0, 0, 0, 0),
    )


def create_mt_release_gesture() -> models.GestureEvent:
    """Create a multi-touch release gesture."""
    gesture = create_mt_hold_gesture()
    gesture.type = enums.GestureType.MULTI_TOUCH_RELEASE
    return gesture


class TestMultiTouchHoldBehaviorInitialization:
    """Test MultiTouchHoldBehavior initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior(
            on_hold=_on_hold, on_release=_on_release
        )

        assert behavior._on_hold_callback is _on_hold
        assert behavior._on_release_callback is _on_release
        assert not behavior.is_active

    def test_init_argument_signatures_unittest(self) -> None:
        """Behavior accepts callback signatures."""

        @multi_touch_hold.behavior_action
        def _on_hold2(arg1: component.Component) -> None: ...
        @multi_touch_hold.behavior_action
        def _on_release2(arg1: component.Component) -> None: ...

        behavior = multi_touch_hold.MultiTouchHoldBehavior(
            on_hold=_on_hold2, on_release=_on_release2
        )

        assert behavior._on_hold_callback is _on_hold2
        assert behavior._on_release_callback is _on_release2


class TestMultiTouchHoldBehaviorHandleGesture:
    """Test MultiTouchHoldBehavior handle_gesture."""

    def test_handle_hold_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle multi-touch hold gesture."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior()
        mock_on_hold = mocker.patch.object(
            behavior, "_on_hold", return_value=None
        )
        mock_component = mocker.Mock()
        gesture = create_mt_hold_gesture()

        behavior.handle_gesture(mock_component, gesture)

        assert behavior.is_active
        mock_on_hold.assert_called_once_with(mock_component, gesture)

    def test_handle_hold_gesture_already_holding_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle multi-touch hold gesture when already holding."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior()
        behavior.is_active = True
        mock_on_hold = mocker.patch.object(
            behavior, "_on_hold", return_value=None
        )

        behavior.handle_gesture(mocker.Mock(), create_mt_hold_gesture())

        assert behavior.is_active
        mock_on_hold.assert_not_called()

    def test_handle_release_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle multi-touch release gesture."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior()
        behavior.is_active = True
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )
        mock_component = mocker.Mock()
        gesture = create_mt_release_gesture()

        behavior.handle_gesture(mock_component, gesture)

        assert not behavior.is_active
        mock_on_release.assert_called_once_with(mock_component, gesture)

    def test_handle_release_gesture_already_released_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle multi-touch release gesture when already released."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior()
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )

        behavior.handle_gesture(mocker.Mock(), create_mt_release_gesture())

        assert not behavior.is_active
        mock_on_release.assert_not_called()


class TestMultiTouchHoldBehaviorOnHold:
    """Test MultiTouchHoldBehavior _on_hold."""

    def test_on_hold_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On hold calls callback."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior(on_hold=_on_hold)
        mock_safe_call = mocker.patch.object(behavior, "_safe_call")
        mock_component = mocker.Mock()
        gesture = create_mt_hold_gesture()

        behavior._on_hold(mock_component, gesture)

        mock_safe_call.assert_called_once_with(
            _on_hold, mock_component, gesture
        )

    def test_on_hold_skips_none_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On hold skips when callback is None."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior()

        # Does not raise error
        behavior._on_hold(mocker.Mock(), create_mt_hold_gesture())


class TestMultiTouchHoldBehaviorOnRelease:
    """Test MultiTouchHoldBehavior _on_release."""

    def test_on_release_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On release calls callback."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior(
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
        behavior = multi_touch_hold.MultiTouchHoldBehavior()

        # Does not raises error
        behavior._on_release(mocker.Mock(), create_mt_release_gesture())
