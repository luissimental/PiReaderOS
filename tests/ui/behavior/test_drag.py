import pytest_mock

from pireaderos.common import enums, models
from pireaderos.ui import component
from pireaderos.ui.behavior import drag


@drag.behavior_action
def _on_touch_down(
    arg1: component.Component, arg2: models.GestureEvent
) -> None: ...


@drag.behavior_action
def _on_drag(arg1: component.Component, arg2: models.GestureEvent) -> None: ...


@drag.behavior_action
def _on_release(
    arg1: component.Component, arg2: models.GestureEvent
) -> None: ...


def create_drag_gesture() -> models.GestureEvent:
    """Create a drag GestureEvent."""
    return models.GestureEvent(
        type=enums.GestureType.DRAG,
        start_point=models.TouchPoint(0, 0, 0, 0),
        end_point=models.TouchPoint(0, 0, 0, 0),
    )


def create_release_gesture() -> models.GestureEvent:
    """Create a release GestureEvent."""
    gesture = create_drag_gesture()
    gesture.type = enums.GestureType.RELEASE
    return gesture


class TestDragBehaviorInitialization:
    """Test DragBehavior initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        behavior = drag.DragBehavior(
            on_touch_down=_on_touch_down,
            on_drag=_on_drag,
            on_release=_on_release,
        )

        assert behavior._on_touch_down_callback is _on_touch_down
        assert behavior._on_drag_callback is _on_drag
        assert behavior._on_release_callback is _on_release
        assert not behavior._is_active

    def test_init_argument_signatures_unittest(self) -> None:
        """Behavior accepts callback signatures."""

        @drag.behavior_action
        def _on_touch_down2(arg1: component.Component) -> None: ...
        @drag.behavior_action
        def _on_drag2(arg1: component.Component) -> None: ...
        @drag.behavior_action
        def _on_release2(arg1: component.Component) -> None: ...

        behavior = drag.DragBehavior(
            on_touch_down=_on_touch_down2,
            on_drag=_on_drag2,
            on_release=_on_release2,
        )

        assert behavior._on_touch_down_callback is _on_touch_down2
        assert behavior._on_drag_callback is _on_drag2
        assert behavior._on_release_callback is _on_release2


class TestDragBehaviorHandleGesture:
    """Test DragBehavior handle_gesture."""

    def test_handle_drag_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle drag gesture."""
        behavior = drag.DragBehavior()
        behavior._is_active = True
        mock_on_drag = mocker.patch.object(
            behavior, "_on_drag", return_value=None
        )
        mock_component = mocker.Mock()
        gesture = create_drag_gesture()

        behavior.handle_gesture(mock_component, gesture)

        assert behavior._is_active
        mock_on_drag.assert_called_once_with(mock_component, gesture)

    def test_handle_drag_gesture_already_dragging_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle drag gesture when already dragging."""
        behavior = drag.DragBehavior()
        behavior._is_active = True
        mock_on_drag = mocker.patch.object(
            behavior, "_on_drag", return_value=None
        )
        mock_component = mocker.Mock()
        gesture = create_drag_gesture()

        behavior.handle_gesture(mock_component, gesture)

        assert behavior._is_active
        mock_on_drag.assert_called_once_with(mock_component, gesture)

    def test_handle_release_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle release gesture."""
        behavior = drag.DragBehavior()
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
        behavior = drag.DragBehavior()
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )

        behavior.handle_gesture(mocker.Mock(), create_release_gesture())

        assert not behavior._is_active
        mock_on_release.assert_not_called()


class TestDragBehaviorOnDrag:
    """Test DragBehavior _on_drag."""

    def test_on_drag_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On drag calls callback."""
        behavior = drag.DragBehavior(on_drag=_on_drag)
        mock_safe_call = mocker.patch.object(behavior, "_safe_call")
        mock_component = mocker.Mock()
        gesture = create_drag_gesture()

        behavior._on_drag(mock_component, gesture)

        mock_safe_call.assert_called_once_with(
            _on_drag, mock_component, gesture
        )

    def test_on_drag_skips_none_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On drag skips when callback is None."""
        behavior = drag.DragBehavior()

        # Does not raise error
        behavior._on_drag(mocker.Mock(), create_drag_gesture())


class TestDragBehaviorOnRelease:
    """Test DragBehavior _on_release."""

    def test_on_release_calls_callback_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """On release calls callback."""
        behavior = drag.DragBehavior(on_release=_on_release)
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
        behavior = drag.DragBehavior()

        # Does not raise error
        behavior._on_release(mocker.Mock(), create_release_gesture())
