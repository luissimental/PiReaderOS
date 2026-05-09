import pytest_mock

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import hold


@hold.behavior_action
def _on_touch_down(
    arg1: component.Component, arg2: models.GestureEvent
) -> None: ...


@hold.behavior_action
def _on_hold(arg1: component.Component, arg2: models.GestureEvent) -> None: ...


@hold.behavior_action
def _on_release(
    arg1: component.Component, arg2: models.GestureEvent
) -> None: ...


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

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        behavior = hold.HoldBehavior(
            on_touch_down=_on_touch_down,
            on_hold=_on_hold,
            on_release=_on_release,
        )

        assert behavior._on_touch_down_callback is _on_touch_down
        assert behavior._on_hold_callback is _on_hold
        assert behavior._on_release_callback is _on_release
        assert not behavior._is_active

    def test_init_argument_signatures_unittest(self) -> None:
        """Behavior accepts callback signatures."""

        @hold.behavior_action
        def _on_touch_down2(arg1: component.Component) -> None: ...
        @hold.behavior_action
        def _on_hold2(arg1: component.Component) -> None: ...
        @hold.behavior_action
        def _on_release2(arg1: component.Component) -> None: ...

        behavior = hold.HoldBehavior(
            on_touch_down=_on_touch_down2,
            on_hold=_on_hold2,
            on_release=_on_release2,
        )

        assert behavior._on_touch_down_callback is _on_touch_down2
        assert behavior._on_hold_callback is _on_hold2
        assert behavior._on_release_callback is _on_release2


class TestHoldBehaviorHandleGesture:
    """Test HoldBehavior handle_gesture."""

    def test_handle_hold_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle hold gesture."""
        behavior = hold.HoldBehavior()
        behavior._is_active = True
        mock_on_hold = mocker.patch.object(
            behavior, "_on_hold", return_value=None
        )
        mock_component = mocker.Mock()
        gesture = create_hold_gesture()

        behavior.handle_gesture(mock_component, gesture)

        assert not behavior._is_active
        mock_on_hold.assert_called_once_with(mock_component, gesture)

    def test_handle_hold_gesture_already_holding_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle hold gesture when already holding."""
        behavior = hold.HoldBehavior()
        mock_on_hold = mocker.patch.object(
            behavior, "_on_hold", return_value=None
        )

        behavior.handle_gesture(mocker.Mock(), create_hold_gesture())

        assert not behavior._is_active
        mock_on_hold.assert_not_called()

    def test_handle_release_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle release gesture."""
        behavior = hold.HoldBehavior()
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
        """Handle release gesture when already released."""
        behavior = hold.HoldBehavior()
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )

        behavior.handle_gesture(mocker.Mock(), create_release_gesture())

        assert not behavior._is_active
        mock_on_release.assert_not_called()


class TestHoldBehaviorOnHold:
    """Test HoldBehavior _on_hold."""

    def test_on_hold_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On hold calls callback."""
        behavior = hold.HoldBehavior(on_hold=_on_hold)
        mock_safe_call = mocker.patch.object(behavior, "_safe_call")
        mock_component = mocker.Mock()
        gesture = create_hold_gesture()

        behavior._on_hold(mock_component, gesture)

        mock_safe_call.assert_called_once_with(
            _on_hold, mock_component, gesture
        )

    def test_on_hold_skips_none_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On hold skips when callback is None."""
        behavior = hold.HoldBehavior()

        # Does not raise error
        behavior._on_hold(mocker.Mock(), create_hold_gesture())


class TestHoldBehaviorOnRelease:
    """Test HoldBehavior _on_release."""

    def test_on_release_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On release calls callback."""
        behavior = hold.HoldBehavior(on_release=_on_release)
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
        behavior = hold.HoldBehavior()

        # Does not raise error
        behavior._on_release(mocker.Mock(), create_release_gesture())
