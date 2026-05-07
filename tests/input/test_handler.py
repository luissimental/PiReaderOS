import queue

import pytest
import pytest_mock

from pireaderos.common import constants, enums, models
from pireaderos.input import handler


@pytest.fixture
def patched_handler(mocker: pytest_mock.MockerFixture) -> handler.InputHandler:
    """Return an InputHandler with dependencies patched."""
    mocker.patch("pireaderos.input.handler.touch.TouchDriver")
    mocker.patch("pireaderos.input.handler.engine.GestureEngine")
    mocker.patch("pireaderos.input.handler.resolver.GestureResolver")
    return handler.InputHandler(mocker.Mock())


@pytest.fixture
def driver_patched_handler(
    mocker: pytest_mock.MockerFixture,
) -> handler.InputHandler:
    """Return an InputHandler with TouchDriver patched."""
    mocker.patch("pireaderos.input.handler.touch.TouchDriver")
    return handler.InputHandler(mocker.Mock())


class TestInputHandlerInitialization:
    """Test InputHandler initialization."""

    def test_init_is_working_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """All attributes are present."""
        mock_hw = mocker.Mock()
        mock_driver = mocker.patch(
            "pireaderos.input.handler.touch.TouchDriver"
        )
        mock_engine = mocker.patch(
            "pireaderos.input.handler.engine.GestureEngine"
        )
        mock_resolver = mocker.patch(
            "pireaderos.input.handler.resolver.GestureResolver"
        )

        hdlr = handler.InputHandler(mock_hw)

        mock_driver.assert_called_once_with(mock_hw, hdlr._on_touch_callback)
        mock_engine.assert_called_once()
        mock_resolver.assert_called_once()
        assert isinstance(hdlr._queue, queue.Queue)


class TestInputHandlerOnTouchCallback:
    """Test InputHandler _on_touch_callback."""

    def test_touch_queues_resolved_gesture_unittest(
        self, patched_handler: pytest_mock.MockType
    ) -> None:
        """Queue resolved gesture."""
        touches = [models.TouchPoint(0, 0, 0, 0)]
        engine = patched_handler._engine
        resolver = patched_handler._resolver
        queue_ = patched_handler._queue

        patched_handler._on_touch_callback(touches)

        engine.process_touch_points.assert_called_once_with(touches)
        resolver.resolve_potential_candidates.assert_called_once_with(
            engine.process_touch_points.return_value
        )
        assert not queue_.empty()
        assert (
            queue_.get_nowait()
            is resolver.resolve_potential_candidates.return_value
        )
        assert queue_.empty()

    def test_touch_queues_resolved_gesture_integration(
        self,
        mocker: pytest_mock.MockerFixture,
        driver_patched_handler: handler.InputHandler,
    ) -> None:
        """Queue resolved gesture."""
        mocker.patch.object(constants.GestureThreshold, "HOLD_TIME", 1)
        mocker.patch.object(constants.GestureThreshold, "HOLD_DISTANCE", 1)
        touches1 = [models.TouchPoint(0, 0, 0, 0)]  # down
        touches2 = [models.TouchPoint(0, 0, 0, 0)]  # contact
        touches3 = [models.TouchPoint(0, 0, 0, 1)]  # holding

        driver_patched_handler._on_touch_callback(touches1)
        driver_patched_handler._on_touch_callback(touches2)
        driver_patched_handler._on_touch_callback(touches3)

        assert not driver_patched_handler._queue.empty()
        gesture = driver_patched_handler._queue.get_nowait()
        assert gesture.type is enums.GestureType.TOUCH_DOWN

        assert not driver_patched_handler._queue.empty()
        gesture = driver_patched_handler._queue.get_nowait()
        assert gesture.type is enums.GestureType.HOLD
        assert driver_patched_handler._queue.empty()

    def test_touch_does_not_queue_none_gesture_unittest(
        self, patched_handler: pytest_mock.MockType
    ) -> None:
        """Does not queue a None resolved gesture."""
        touches = [models.TouchPoint(0, 0, 0, 0)]
        engine = patched_handler._engine
        resolver = patched_handler._resolver
        resolver.resolve_potential_candidates.return_value = None
        queue_ = patched_handler._queue

        patched_handler._on_touch_callback(touches)

        engine.process_touch_points.assert_called_once_with(touches)
        resolver.resolve_potential_candidates.assert_called_once_with(
            engine.process_touch_points.return_value
        )
        assert queue_.empty()

    def test_touch_does_not_queue_none_gesture_integration(
        self,
        mocker: pytest_mock.MockerFixture,
        driver_patched_handler: handler.InputHandler,
    ) -> None:
        """Does not queue a None resolved gesture."""
        mocker.patch.object(constants.GestureThreshold, "HOLD_TIME", 1000)
        mocker.patch.object(constants.GestureThreshold, "HOLD_DISTANCE", 1000)
        touches1 = []

        driver_patched_handler._on_touch_callback(touches1)

        assert driver_patched_handler._queue.empty()


class TestInputHandlerPollForGesture:
    """Test Input Handler poll_for_gesture."""

    def test_poll_returns_timed_gesture_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        patched_handler: pytest_mock.MockType,
    ) -> None:
        """Return queued timed gesture."""
        mock_timed_gesture = mocker.Mock()
        resolver = patched_handler._resolver
        resolver.poll_timed_gestures.return_value = mock_timed_gesture
        queue_ = patched_handler._queue

        gesture = patched_handler.poll_for_gesture()

        resolver.poll_timed_gestures.assert_called_once()
        assert queue_.empty()
        assert gesture is mock_timed_gesture

    def test_poll_returns_queued_gesture_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        patched_handler: pytest_mock.MockType,
    ) -> None:
        """Return queued non-timed gesture."""
        mock_gesture = mocker.Mock()
        resolver = patched_handler._resolver
        resolver.poll_timed_gestures.return_value = None
        queue_ = patched_handler._queue
        queue_.put_nowait(mock_gesture)

        gesture = patched_handler.poll_for_gesture()

        resolver.poll_timed_gestures.assert_called_once()
        assert queue_.empty()
        assert gesture is mock_gesture

    def test_poll_returns_all_queued_gestures_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        patched_handler: pytest_mock.MockType,
    ) -> None:
        """Return all queued gestures."""
        mock_gesture1 = mocker.Mock()
        mock_gesture2 = mocker.Mock()
        mock_gesture3 = mocker.Mock()
        mock_timed_gesture = mocker.Mock()
        queue_ = patched_handler._queue
        queue_.put_nowait(mock_gesture1)
        queue_.put_nowait(mock_gesture2)
        queue_.put_nowait(mock_gesture3)
        resolver = patched_handler._resolver
        resolver.poll_timed_gestures.return_value = mock_timed_gesture

        gesture1 = patched_handler.poll_for_gesture()
        resolver.poll_timed_gestures.return_value = None
        gesture2 = patched_handler.poll_for_gesture()
        gesture3 = patched_handler.poll_for_gesture()
        timed_gesture = patched_handler.poll_for_gesture()

        assert queue_.empty()
        assert gesture1 is mock_gesture1
        assert gesture2 is mock_gesture2
        assert gesture3 is mock_gesture3
        assert timed_gesture is mock_timed_gesture

    def test_poll_returns_none_on_no_queued_unittest(
        self, patched_handler: pytest_mock.MockType
    ) -> None:
        """Return None when there are no queued gestures."""
        resolver = patched_handler._resolver
        resolver.poll_timed_gestures.return_value = None

        gesture = patched_handler.poll_for_gesture()

        assert gesture is None
