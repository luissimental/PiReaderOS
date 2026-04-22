import queue

from pireaderos.hal import manager
from pireaderos.hardware import models as hw_models
from pireaderos.hardware import touch
from pireaderos.input import engine, models, resolver


class InputHandler:
    """Handler for generating gestures from touch input.

    Frequent polling is required to receive valid gestures, including immediate
    and delayed emissions. Delayed emissions are for gestures that require
    further processing on subsequent touch events.

    For example, a TAP gesture is an immediate emission for lightweight
    feedback (ex. okay button). However, complex actions that cannot be
    registered when the tap count increases (ex. zooming) are detected with
    DELAYED TAP gestures for disambiguation.

    Attributes:
      driver:
        The touch controller driver. Can be managed for resetting, setting the
        power mode, and cleaning up.

    Example:
      Poll to receive gestures (used with a HardwareManager)::

        with HardwareManager() as hw:
            input_handler = InputHandler(hw)
            while True:
                gesture = input_handler.poll_for_gesture()
                if gesture:
                    # Process gesture
                time.sleep(0.02)

    """

    def __init__(self, hw: manager.HardwareManager) -> None:
        self.driver = touch.TouchDriver(hw, self._on_touch_callback)
        self._engine = engine.GestureEngine()
        self._resolver = resolver.GestureResolver()
        self._queue: queue.Queue[models.GestureEvent] = queue.Queue()

    def _on_touch_callback(self, touches: list[hw_models.TouchPoint]) -> None:
        """Interrupt callback for processing touch data into gestures.

        Valid gestures are put into a queue for emission.

        Args:
          touches:
            A list of touch points from the touch controller for processing.

        """
        candidates = self._engine.process_touch_points(touches)
        gesture = self._resolver.resolve_potential_candidates(candidates)
        if gesture is not None:
            self._queue.put_nowait(gesture)

    def poll_for_gesture(self) -> models.GestureEvent | None:
        """Frequently poll for gestures.

        Returns:
          A valid gesture from the touch controller. May be None if no gesture
          has been detected yet.

        """
        timed_gesture = self._resolver.poll_timed_gestures()
        if timed_gesture is not None:
            self._queue.put_nowait(timed_gesture)

        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None
