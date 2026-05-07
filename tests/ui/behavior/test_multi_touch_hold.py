import pytest
import pytest_mock

from pireaderos.hardware import models as hw_models
from pireaderos.input import enums, models
from pireaderos.ui.behavior import multi_touch_hold


@pytest.fixture
def on_hold(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock an on_hold callback."""
    return mocker.Mock()


@pytest.fixture
def on_release(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock an on_release callback."""
    return mocker.Mock()


def create_mt_hold_gesture() -> models.GestureEvent:
    """Create a multi-touch hold gesture."""
    return models.GestureEvent(
        type=enums.GestureType.MULTI_TOUCH_HOLD,
        start_point=hw_models.TouchPoint(0, 0, 0, 0),
        end_point=hw_models.TouchPoint(0, 0, 0, 0),
    )


def create_mt_release_gesture() -> models.GestureEvent:
    """Create a multi-touch release gesture."""
    gesture = create_mt_hold_gesture()
    gesture.type = enums.GestureType.MULTI_TOUCH_RELEASE
    return gesture


class TestMultiTouchHoldBehaviorInitialization:
    """Test MultiTouchHoldBehavior initialization."""

    def test_init_is_working_unittest(
        self, on_hold: pytest_mock.MockType, on_release: pytest_mock.MockType
    ) -> None:
        """All attributes are present."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior(
            on_hold=on_hold, on_release=on_release
        )

        assert behavior._on_hold_callback is on_hold
        assert behavior._on_release_callback is on_release


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
        gesture = create_mt_hold_gesture()

        behavior.handle_gesture(gesture)

        assert behavior._is_holding
        mock_on_hold.assert_called_once_with(gesture)

    def test_handle_hold_gesture_already_holding_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle multi-touch hold gesture when already holding."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior()
        behavior._is_holding = True
        mock_on_hold = mocker.patch.object(
            behavior, "_on_hold", return_value=None
        )
        gesture = create_mt_hold_gesture()

        behavior.handle_gesture(gesture)

        assert behavior._is_holding
        mock_on_hold.assert_not_called()

    def test_handle_release_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle multi-touch release gesture."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior()
        behavior._is_holding = True
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )
        gesture = create_mt_release_gesture()

        behavior.handle_gesture(gesture)

        assert not behavior._is_holding
        mock_on_release.assert_called_once_with(gesture)

    def test_handle_release_gesture_already_released_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Handle multi-touch release gesture when already released."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior()
        mock_on_release = mocker.patch.object(
            behavior, "_on_release", return_value=None
        )

        behavior.handle_gesture(create_mt_release_gesture())

        assert not behavior._is_holding
        mock_on_release.assert_not_called()


class TestMultiTouchHoldBehaviorOnHold:
    """Test MultiTouchHoldBehavior _on_hold."""

    def test_on_hold_calls_callback_unittest(
        self, on_hold: pytest_mock.MockType
    ) -> None:
        """On hold calls callback."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior(on_hold=on_hold)
        gesture = create_mt_hold_gesture()

        behavior._on_hold(gesture)

        on_hold.assert_called_once_with(gesture)

    def test_on_hold_skips_none_callback_unittest(self) -> None:
        """On hold skips when callback is None."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior()

        behavior._on_hold(create_mt_hold_gesture())  # does not raise error


class TestMultiTouchHoldBehaviorOnRelease:
    """Test MultiTouchHoldBehavior _on_release."""

    def test_on_release_calls_callback_unittest(
        self, on_release: pytest_mock.MockType
    ) -> None:
        """On release calls callback."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior(
            on_release=on_release
        )
        gesture = create_mt_release_gesture()

        behavior._on_release(gesture)

        on_release.assert_called_once_with(gesture)

    def test_on_release_skips_none_callback_unittest(self) -> None:
        """On release skips when callback is None."""
        behavior = multi_touch_hold.MultiTouchHoldBehavior()

        # Does not raises error
        behavior._on_release(create_mt_release_gesture())
