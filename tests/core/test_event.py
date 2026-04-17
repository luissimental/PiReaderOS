from collections.abc import Callable

import pytest
import pytest_mock

from pireaderos.core import event


@pytest.fixture
def mock_function_with_name(
    mocker: pytest_mock.MockerFixture,
) -> Callable[..., pytest_mock.MockType]:
    """Create factory fixture to return a mock with __name__ attribute."""

    def _mock_func() -> pytest_mock.MockType:
        mock = mocker.MagicMock()
        mock.__name__ = "FuncName"
        return mock

    return _mock_func


class TestEventManagerInitialization:
    """Test EventManager initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        events = event.EventManager()

        assert type(events._event_to_subs) is dict
        assert not events._event_to_subs


class TestEventManagerSubscribe:
    """Test EventManager subscribe."""

    def test_valid_callback_subscribes_to_nonexisting_valid_event_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Subscribe callback to event successfully.

        When event does not exist yet.
        """
        mock_callback = mock_function_with_name()
        events = event.EventManager()

        events.subscribe("MockEvent", mock_callback)

        subscribers = events._event_to_subs.get("MockEvent")
        assert type(subscribers) is set
        assert len(subscribers) == 1
        assert mock_callback in subscribers

    def test_valid_callback_subscribes_to_existing_valid_event_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Subscribe callback to event successfully.

        When event exists and callback is not subscribed to event.
        """
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback1}}

        events.subscribe("MockEvent", mock_callback2)

        subscribers = events._event_to_subs.get("MockEvent")
        assert type(subscribers) is set
        assert len(subscribers) == 2
        assert mock_callback1 in subscribers
        assert mock_callback2 in subscribers

    def test_valid_callback_subscribes_to_multiple_existing_valid_events_unittest(
        self,
        mock_function_with_name: Callable[..., pytest_mock.MockType],
    ) -> None:
        """Subscribe callback to multiple existing events successfully."""
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        mock_callback3 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {
            "MockEvent1": {mock_callback1},
            "MockEvent2": {mock_callback2},
        }

        events.subscribe("MockEvent1", mock_callback3)

        subscribers = events._event_to_subs.get("MockEvent1")
        assert type(subscribers) is set
        assert len(subscribers) == 2
        assert mock_callback1 in subscribers
        assert mock_callback3 in subscribers

        events.subscribe("MockEvent2", mock_callback3)

        subscribers = events._event_to_subs.get("MockEvent2")
        assert type(subscribers) is set
        assert len(subscribers) == 2
        assert mock_callback2 in subscribers
        assert mock_callback3 in subscribers

    def test_valid_callback_doesnt_subscribe_to_event_already_subscribed_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Subscribe callback to event fails.

        Callback is already subscribed.
        """
        mock_callback = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback}}

        events.subscribe("MockEvent", mock_callback)

        subscribers = events._event_to_subs.get("MockEvent")
        assert type(subscribers) is set
        assert len(subscribers) == 1
        assert mock_callback in subscribers

    @pytest.mark.parametrize("event_name", [None, 1, object()])
    def test_valid_callback_doesnt_subscribe_to_invalid_event_type_unittest(
        self,
        mock_function_with_name: Callable[..., pytest_mock.MockType],
        event_name: object,
    ) -> None:
        """Subscribe callback to event fails.

        Event_name is not a string.
        """
        mock_callback = mock_function_with_name()
        events = event.EventManager()
        original_dict = events._event_to_subs

        events.subscribe(event_name, mock_callback)  # pyright: ignore[reportArgumentType]

        assert events._event_to_subs is original_dict

    @pytest.mark.parametrize("callback", [None, 1, object()])
    def test_invalid_callback_type_doesnt_subscribe_to_nonexisting_valid_event_unittest(
        self, callback: object
    ) -> None:
        """Subscribe callback to nonexisting event fails.

        Callback is not callable.
        """
        events = event.EventManager()
        original_dict = events._event_to_subs

        events.subscribe("MockEvent", callback)  # pyright: ignore[reportArgumentType]

        assert events._event_to_subs is original_dict

    @pytest.mark.parametrize("callback", [None, 1, object()])
    def test_invalid_callback_type_doesnt_subscribe_to_existing_valid_event_unittest(
        self,
        mock_function_with_name: Callable[..., pytest_mock.MockType],
        callback: object,
    ) -> None:
        """Subscribe callback to existing event fails.

        Callback is not callable.
        """
        mock_callback = mock_function_with_name()
        mock_events_dict = {"MockEvent": {mock_callback}}
        events = event.EventManager()
        events._event_to_subs = mock_events_dict

        events.subscribe("MockEvent", callback)  # pyright: ignore[reportArgumentType]

        assert events._event_to_subs is mock_events_dict


class TestEventManagerUnsubscribe:
    """Test EventManager unsubscribe."""

    def test_valid_callback_unsubscribes_from_existing_valid_event_with_multiple_subs_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Unsubscribe callback from event successfully.

        When event has multiple subscribers.
        """
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback1, mock_callback2}}

        events.unsubscribe("MockEvent", mock_callback2)

        subscribers = events._event_to_subs.get("MockEvent")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback1 in subscribers

    def test_valid_callback_unsubscribes_from_existing_valid_event_with_one_sub_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Unsubscribe callback from event successfully.

        When callback is the only subscriber.
        """
        mock_callback = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback}}

        events.unsubscribe("MockEvent", mock_callback)

        subscribers = events._event_to_subs.get("MockEvent")
        assert subscribers is None

    def test_valid_callback_unsubscribes_from_multiple_existing_events_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Unsubscribe callback from multiple events successfully."""
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        mock_callback3 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {
            "MockEvent1": {mock_callback1, mock_callback3},
            "MockEvent2": {mock_callback2, mock_callback3},
        }

        events.unsubscribe("MockEvent1", mock_callback3)

        subscribers = events._event_to_subs.get("MockEvent1")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback1 in subscribers

        events.unsubscribe("MockEvent2", mock_callback3)

        subscribers = events._event_to_subs.get("MockEvent2")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback2 in subscribers

    def test_valid_callback_doesnt_unsubscribe_from_nonexistant_valid_event_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Unsubscribe callback from event fails when event does not exist."""
        mock_callback = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback}}

        events.unsubscribe("NotExistant", mock_callback)

        subscribers = events._event_to_subs.get("MockEvent")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback in subscribers

    def test_valid_callback_doesnt_unsubscribe_from_existing_event_not_subscribed_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Unsubscribe callback from event fails.

        Callback is not subscribed to event.
        """
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback1}}

        events.unsubscribe("MockEvent", mock_callback2)

        subscribers = events._event_to_subs.get("MockEvent")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback1 in subscribers

    @pytest.mark.parametrize("event_name", [None, 1, object()])
    def test_valid_callback_doesnt_unsubscribe_from_invalid_event_type_unittest(
        self,
        mock_function_with_name: Callable[..., pytest_mock.MockType],
        event_name: object,
    ) -> None:
        """Unsubscribe callback from event fails.

        Event_name is not a string.
        """
        mock_callback = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback}}

        events.unsubscribe(event_name, mock_callback)  # pyright: ignore[reportArgumentType]

        subscribers = events._event_to_subs.get("MockEvent")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback in subscribers

    @pytest.mark.parametrize("callback", [None, 1, object()])
    def test_invalid_callback_doesnt_unsubscribe_from_event_unittest(
        self,
        mock_function_with_name: Callable[..., pytest_mock.MockType],
        callback: object,
    ) -> None:
        """Unsubscribe callback from event fails.

        Callback is not callable.
        """
        mock_callback = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback}}

        events.unsubscribe("MockEvent", callback)  # pyright: ignore[reportArgumentType]

        subscribers = events._event_to_subs.get("MockEvent")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback in subscribers


class TestEventManagerUnsubscribeAll:
    """Test EventManager unsubscribe_all."""

    def test_valid_callback_unsubscribes_from_one_event_with_multiple_subs_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Unsubscribe callback from all events successfully.

        When callback is only subscribed to one event that contains multiple
        subscribers.
        """
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback1, mock_callback2}}

        events.unsubscribe_all(mock_callback2)

        subscribers = events._event_to_subs.get("MockEvent")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback1 in subscribers

    def test_valid_callback_unsubscribes_from_one_event_with_one_sub_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Unsubscribe callback from all events successfully.

        When callback is only subscribed to one event that contains one
        subscriber.
        """
        mock_callback = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback}}

        events.unsubscribe_all(mock_callback)

        subscribers = events._event_to_subs.get("MockEvent")
        assert subscribers is None

    def test_valid_callback_unsubscribes_from_multiple_events_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Unsubscribe callback from all events successfully.

        When callback is subscribed to multiple events.
        """
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        mock_callback3 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {
            "MockEvent1": {mock_callback1, mock_callback3},
            "MockEvent2": {mock_callback2, mock_callback3},
        }

        events.unsubscribe_all(mock_callback3)

        subscribers = events._event_to_subs.get("MockEvent1")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback1 in subscribers

        subscribers = events._event_to_subs.get("MockEvent2")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback2 in subscribers

    def test_valid_callback_doesnt_unsubscribe_from_event_not_subscribed_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Unsubscribe callback from all events fails.

        Callback is not subscribed to any events.
        """
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback1}}

        events.unsubscribe_all(mock_callback2)

        subscribers = events._event_to_subs.get("MockEvent")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback1 in subscribers

    @pytest.mark.parametrize("callback", [None, 1, object()])
    def test_invalid_callback_doesnt_unsubscribe_unittest(
        self,
        mock_function_with_name: Callable[..., pytest_mock.MockType],
        callback: object,
    ) -> None:
        """Unsubscribe callback from all events fails.

        Callback is not callable.
        """
        mock_callback = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {"MockEvent": {mock_callback}}

        events.unsubscribe_all(callback)  # pyright: ignore[reportArgumentType]

        subscribers = events._event_to_subs.get("MockEvent")
        assert subscribers is not None
        assert len(subscribers) == 1
        assert mock_callback in subscribers


class TestEventManagerEmitEvent:
    """Test EventManager emit."""

    def test_event_emits_to_all_subscribers_and_calls_with_proper_no_args_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Emit event to subscribers successfully.

        When callbacks do not need args.
        """
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {
            "MockEvent1": {mock_callback1, mock_callback2},
            "MockEvent2": {mock_callback2},
        }

        events.emit("MockEvent1")

        mock_callback1.assert_called_once()
        mock_callback2.assert_called_once()

    def test_event_emits_to_all_subscribers_and_calls_with_proper_args_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Emit event to subscribers successfully.

        When callbacks require args.
        """
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {
            "MockEvent1": {mock_callback1, mock_callback2},
            "MockEvent2": {mock_callback2},
        }

        events.emit("MockEvent1", "a1", "a2", kw1="k1")

        mock_callback1.assert_called_once_with("a1", "a2", kw1="k1")
        mock_callback2.assert_called_once_with("a1", "a2", kw1="k1")

    def test_event_attempts_to_emit_to_subscribers_with_improper_args_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Emit event to subscribers fails.

        Callbacks are called with invalid args.
        """
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        mock_callback1.side_effect = TypeError
        mock_callback2.side_effect = TypeError
        events = event.EventManager()
        events._event_to_subs = {
            "MockEvent1": {mock_callback1, mock_callback2},
            "MockEvent2": {mock_callback2},
        }

        events.emit("MockEvent1", "a2", kw1="k1")  # TypeError is handled

        mock_callback1.assert_called_once_with("a2", kw1="k1")
        mock_callback2.assert_called_once_with("a2", kw1="k1")

    def test_event_attempts_to_emit_to_subscribers_with_improper_args_integration(
        self,
    ) -> None:
        """Emit event to subscribers fails.

        Callbacks are called with invalid args.
        """
        must_not_be_called = []

        def callback1(a1, a2, kw1=None) -> None:  # noqa: ANN001, ARG001
            must_not_be_called.append(1)

        def callback2(a1, a2, kw1=None) -> None:  # noqa: ANN001, ARG001
            must_not_be_called.append(2)

        events = event.EventManager()
        events._event_to_subs = {
            "Event1": {callback1, callback2},
            "Event2": {callback2},
        }

        events.emit("Event1", "a2", kw1="k1")  # TypeError is handled

        assert len(must_not_be_called) == 0

    def test_event_doesnt_exist_no_subscribers_called_unittest(
        self, mock_function_with_name: Callable[..., pytest_mock.MockType]
    ) -> None:
        """Emit event to subscribers fails when event does not exist."""
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {
            "MockEvent1": {mock_callback1, mock_callback2},
            "MockEvent2": {mock_callback2},
        }

        events.emit("NonExistant", "a1", "a2", kw1="k1")

        mock_callback1.assert_not_called()
        mock_callback2.assert_not_called()

    @pytest.mark.parametrize("event_name", [None, 1, object()])
    def test_invalid_event_type_no_subscribers_called_unittest(
        self,
        mock_function_with_name: Callable[..., pytest_mock.MockType],
        event_name: object,
    ) -> None:
        """Emit event to subscribers fails when event_name is not a string."""
        mock_callback1 = mock_function_with_name()
        mock_callback2 = mock_function_with_name()
        events = event.EventManager()
        events._event_to_subs = {
            "MockEvent1": {mock_callback1, mock_callback2},
            "MockEvent2": {mock_callback2},
        }

        events.emit(event_name, "a1", "a2", kw1="k1")  # pyright: ignore[reportArgumentType]

        mock_callback1.assert_not_called()
        mock_callback2.assert_not_called()
