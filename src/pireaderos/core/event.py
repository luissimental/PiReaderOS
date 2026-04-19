import inspect
import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)


class EventManager:
    """The manager for the event to callback system."""

    def __init__(self) -> None:
        self._event_to_subs: dict[str, set[Callable]] = {}
        logger.info("Initialized 'EventManager'")

    def subscribe(self, event_name: str, callback: Callable) -> None:
        """Register the callback to an event."""
        # Check that the argument types are valid
        if not callable(callback):
            logger.error(
                "Subscribing callback to event '%s' failed. "
                "Callback '%s' is not callable",
                event_name,
                callback,
            )
            return
        if type(event_name) is not str:
            logger.error(
                "Subscribing callback '%s' failed. "
                "Event name '%s' is not a string",
                callback.__name__,
                event_name,
            )
            return

        # Subscribe to event
        subscribers = self._event_to_subs.get(event_name)
        if subscribers is None:
            self._event_to_subs[event_name] = subscribers = set()
        subscribers.add(callback)

        logger.info(
            "Subscribed callback '%s' to event '%s'",
            callback.__name__,
            event_name,
        )

    def unsubscribe(
        self,
        event_name: str,
        callback: Callable,
        _use_dict: dict | None = None,
    ) -> bool:
        """Remove callback from event."""
        # Check that argument types are valid
        if not callable(callback):
            logger.error(
                "Unsubscribing callback to event '%s' failed. "
                "Callback '%s' is not callable",
                event_name,
                callback,
            )
            return False
        if type(event_name) is not str:
            logger.error(
                "Unsubscribing callback '%s' failed. "
                "Event name '%s' is not a string",
                callback.__name__,
                event_name,
            )
            return False

        # Only used for self.unsubscribe_all
        if _use_dict is None:
            event_to_subs_dict = self._event_to_subs
        else:
            event_to_subs_dict = _use_dict

        # Do nothing if event does not exist
        subscribers = event_to_subs_dict.get(event_name)
        if subscribers is None:
            logger.error(
                "Unsubscribing callback '%s' failed. "
                "Event '%s' does not exist",
                callback.__name__,
                event_name,
            )
            return False

        # Unsubscribe from event
        subscribers.discard(callback)
        if len(subscribers) == 0:
            del event_to_subs_dict[event_name]

        logger.info(
            "Unsubscribed callback '%s' from event '%s'",
            callback.__name__,
            event_name,
        )
        return True

    def unsubscribe_all(self, callback: Callable) -> None:
        """Remove callback function from all subscribed events."""
        # Check that argument types are valid
        if not callable(callback):
            logger.error(
                "Unsubscribing callback from all events failed. "
                "Callback '%s' is not callable",
                callback,
            )
            return

        # Loop through events and unsubscribe from all
        logger.info(
            "Unsubscribing callback '%s' from all events...", callback.__name__
        )
        unsubscribed = False
        event_to_subs_copy = self._event_to_subs.copy()
        for event in self._event_to_subs:
            success = self.unsubscribe(event, callback, event_to_subs_copy)
            if success:
                unsubscribed = True
        self._event_to_subs = event_to_subs_copy

        if unsubscribed:
            logger.info(
                "Unsubscribed callback '%s' from all events", callback.__name__
            )
        else:
            logger.error(
                "Unsubscribing callback '%s' from all "
                "events failed. No events subscribed",
                callback.__name__,
            )

    def emit(self, event_name: str, *args: object, **kwargs: object) -> None:
        """Emit event to subscribers with specified args and kwargs."""
        # Check that argument type is valid
        if type(event_name) is not str:
            logger.error(
                "Emitting event failed. Event name '%s' is not a string",
                event_name,
            )
            return

        # Do nothing if event does not exist
        subscribers = self._event_to_subs.get(event_name)
        if subscribers is None:
            logger.error(
                "Emitting event failed. Event '%s' does not exist", event_name
            )
            return

        # Format *args for logging
        args_str = ", ".join(
            [f"'{arg}'" if type(arg) is str else str(arg) for arg in args]
        )
        logger.info(
            "Emitting event '%s' with args: (%s), kwargs: %s...",
            event_name,
            args_str,
            kwargs,
        )

        # Run all subscribers with specified args and kwargs
        for callback in subscribers:
            try:
                logger.info("Running callback '%s'...", callback.__name__)
                callback(*args, **kwargs)
                logger.info(
                    "Running callback '%s' finished", callback.__name__
                )
            except TypeError:
                logger.exception(
                    "TypeError: Running callback '%s' "
                    "with args failed. Signature: %s",
                    callback.__name__,
                    inspect.signature(callback),
                )

        logger.info("Emitting event '%s' finished", event_name)
