import pytest_mock

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import delayed_tap


@delayed_tap.behavior_action
def _on_tap(arg1: component.Component, arg2: models.GestureEvent) -> None: ...


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

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        behavior = delayed_tap.DelayedTapBehavior(on_tap=_on_tap)

        assert behavior._on_tap_callback is _on_tap

    def test_init_argument_signatures_unittest(self) -> None:
        """Behavior accepts callback signatures."""

        @delayed_tap.behavior_action
        def _on_tap2(
            arg1: component.Component, arg2: models.GestureEvent
        ) -> None: ...

        behavior = delayed_tap.DelayedTapBehavior(on_tap=_on_tap2)

        assert behavior._on_tap_callback is _on_tap2


class TestDelayedTapBehaviorHandleGesture:
    """Test DelayedTapBehavior handle_gesture."""

    def test_handle_delayed_tap_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle delayed tap gesture."""
        behavior = delayed_tap.DelayedTapBehavior()
        mock_on_tap = mocker.patch.object(behavior, "_on_tap")
        mock_component = mocker.Mock()
        gesture = create_delayed_tap_gesture()

        behavior.handle_gesture(mock_component, gesture)

        mock_on_tap.assert_called_once_with(mock_component, gesture)

    def test_handle_skips_wrong_gesture_type_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Skip wrong gesture type."""
        behavior = delayed_tap.DelayedTapBehavior()
        mock_on_tap = mocker.patch.object(behavior, "_on_tap")

        behavior.handle_gesture(mocker.Mock(), create_drag_gesture())

        mock_on_tap.assert_not_called()


class TestDelayedTapBehaviorOnTap:
    """Test DelayedTapBehavior _on_tap."""

    def test_on_tap_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On tap calls callback."""
        behavior = delayed_tap.DelayedTapBehavior(on_tap=_on_tap)
        mock_safe_call = mocker.patch.object(behavior, "_safe_call")
        mock_component = mocker.Mock()
        gesture = create_delayed_tap_gesture()

        behavior._on_tap(mock_component, gesture)

        mock_safe_call.assert_called_once_with(
            _on_tap, mock_component, gesture
        )

    def test_on_tap_skips_none_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On hold skips when callback is None."""
        behavior = delayed_tap.DelayedTapBehavior()

        # Does not raise error
        behavior._on_tap(mocker.Mock(), create_delayed_tap_gesture())
