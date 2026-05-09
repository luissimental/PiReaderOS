import pytest_mock

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import swipe


@swipe.behavior_action
def _on_swipe(
    arg1: component.Component, arg2: models.GestureEvent
) -> None: ...


def create_swipe_gesture() -> models.GestureEvent:
    """Create a swipe gesture."""
    return models.GestureEvent(
        type=enums.GestureType.SWIPE,
        start_point=models.TouchPoint(0, 0, 0, 0),
        end_point=models.TouchPoint(0, 0, 0, 0),
    )


def create_drag_gesture() -> models.GestureEvent:
    """Create a drag gesture."""
    gesture = create_swipe_gesture()
    gesture.type = enums.GestureType.DRAG
    return gesture


class TestSwipeBehaviorInitialization:
    """Test SwipeBehavior initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        behavior = swipe.SwipeBehavior(on_swipe=_on_swipe)

        assert behavior._on_swipe_callback is _on_swipe

    def test_init_argument_signatures_unittest(self) -> None:
        """Behavior accepts callback signatures."""

        @swipe.behavior_action
        def _on_swipe2(
            arg1: component.Component, arg2: models.GestureEvent
        ) -> None: ...

        behavior = swipe.SwipeBehavior(on_swipe=_on_swipe2)

        assert behavior._on_swipe_callback is _on_swipe2


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
        mock_component = mocker.Mock()
        gesture = create_swipe_gesture()

        behavior.handle_gesture(mock_component, gesture)

        mock_on_swipe.assert_called_once_with(mock_component, gesture)

    def test_handle_skips_wrong_gesture_type_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Skip wrong gesture type."""
        behavior = swipe.SwipeBehavior()
        mock_on_swipe = mocker.patch.object(
            behavior, "_on_swipe", return_value=None
        )

        behavior.handle_gesture(mocker.Mock(), create_drag_gesture())

        mock_on_swipe.assert_not_called()


class TestSwipeBehaviorOnSwipe:
    """Test SwipeBehavior _on_swipe."""

    def test_on_swipe_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On swipe calls callback."""
        behavior = swipe.SwipeBehavior(on_swipe=_on_swipe)
        mock_safe_call = mocker.patch.object(behavior, "_safe_call")
        mock_component = mocker.Mock()
        gesture = create_swipe_gesture()

        behavior._on_swipe(mock_component, gesture)

        mock_safe_call.assert_called_once_with(
            _on_swipe, mock_component, gesture
        )

    def test_on_swipe_skips_none_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On swipe skips when callback is None."""
        behavior = swipe.SwipeBehavior()

        # Does not raise error
        behavior._on_swipe(mocker.Mock(), create_swipe_gesture())
