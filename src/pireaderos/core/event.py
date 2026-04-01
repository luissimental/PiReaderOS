import logging
from inspect import signature
from typing import Callable


logger = logging.getLogger(__name__)


class EventManager:
    def __init__(self):
        self.event_to_subs: dict[str, set[Callable]] = {}
        logger.info("Initialized 'EventManager'")

    def subscribe(self, event_name: str, callback: Callable):
        """Register a function to be called when an event occurs"""
        # Check that argument types are valid
        if not callable(callback):
            logger.error(
                f"Subscribing callback to event '{event_name}' failed. "
                f"Callback '{callback}' is not callable"
            )
            return
        if type(event_name) is not str:
            logger.error(
                f"Subscribing callback '{callback.__name__}' failed. "
                f"Event name '{event_name}' is not a string"
            )
            return

        # Subscribe to event
        subscribers = self.event_to_subs.get(event_name)
        if subscribers is None:
            self.event_to_subs[event_name] = subscribers = set()
        subscribers.add(callback)

        logger.info(
            f"Subscribed callback '{callback.__name__}' "
            f"to event '{event_name}'"
        )

    def unsubscribe(
        self, event_name: str, callback: Callable,
        _use_dict: dict | None = None
    ):
        """Remove callback function from specified event"""
        # Check that argument types are valid
        if not callable(callback):
            logger.error(
                f"Unsubscribing callback from event '{event_name}' failed. "
                f"Callback '{callback}' is not callable"
            )
            return False
        if type(event_name) is not str:
            logger.error(
                f"Unsubscribing callback '{callback.__name__}' failed. "
                f"Event name '{event_name}' is not a string"
            )
            return False

        # Only used for self.unsubscribe_all
        if _use_dict is None:
            event_to_subs_dict = self.event_to_subs
        else:
            event_to_subs_dict = _use_dict

        # Do nothing if event does not exist
        subscribers = event_to_subs_dict.get(event_name)
        if subscribers is None:
            logger.error(
                f"Unsubscribing callback '{callback.__name__}' failed. "
                f"Event '{event_name}' does not exist"
            )
            return False

        # Unsubscribe from event
        subscribers.discard(callback)
        if len(subscribers) == 0:
            del event_to_subs_dict[event_name]

        logger.info(
            f"Unsubscribed callback '{callback.__name__}' "
            f"from event '{event_name}'")
        return True

    def unsubscribe_all(self, callback: Callable):
        """Remove callback function from all subscribed events"""
        # Check that argument types are valid
        if not callable(callback):
            logger.error(
                "Unsubscribing callback from all events failed. "
                f"Callback '{callback}' is not callable"
            )
            return

        # Loop through events and unsubscribe from all
        logger.info(
            f"Unsubscribing callback '{callback.__name__}' "
            "from all events..."
        )
        unsubscribed = False
        event_to_subs_copy = self.event_to_subs.copy()
        for event in self.event_to_subs:
            success = self.unsubscribe(event, callback, event_to_subs_copy)
            if success:
                unsubscribed = True
        self.event_to_subs = event_to_subs_copy

        if unsubscribed:
            logger.info(
                f"Unsubscribed callback '{callback.__name__}' "
                "from all events"
            )
        else:
            logger.error(
                f"Unsubscribing callback '{callback.__name__}' from all "
                "events failed. No events subscribed"
            )

    def emit(self, event_name: str, *args, **kwargs):
        """Emit event to subscribers with specified args and kwargs"""
        # Check that argument type is valid
        if type(event_name) is not str:
            logger.error(
                "Emitting event failed. "
                f"Event name '{event_name}' is not a string"
            )
            return

        # Do nothing if event does not exist
        subscribers = self.event_to_subs.get(event_name)
        if subscribers is None:
            logger.error(
                "Emitting event failed. "
                f"Event '{event_name}' does not exist"
            )
            return

        # Format *args for logging
        args_str = ", ".join(
            [f"'{arg}'" if type(arg) is str else str(arg) for arg in args])
        logger.info(
            f"Emitting event '{event_name}' "
            f"with args: ({args_str}), kwargs: {kwargs}..."
        )

        # Run all subscribers with specified args and kwargs
        for callback in subscribers:
            try:
                logger.info(f"Running callback '{callback.__name__}'...")
                callback(*args, **kwargs)
                logger.info(
                    f"Running callback '{callback.__name__}' finished")
            except TypeError:
                logger.error(
                    f"TypeError: Running callback '{callback.__name__}' "
                    f"with args failed. Signature: {signature(callback)}"
                )

        logger.info(f"Emitting event '{event_name}' finished")
