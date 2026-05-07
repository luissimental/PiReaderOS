import math
import time

from pireaderos.common import enums, models
from pireaderos.input import constants, geometry


class GestureResolver:
    """Resolve and emit gestures while respecting their lifecycle states.

    Handles priority-based gesture selection when multiple candidates exist.
    Maintains active and timed gesture state to ensure gestures emit correctly:
    lifecycle gestures (HOLD, DRAG, etc.) emit once and update on changes,
    while tap gestures emit both immediately and after a delay to detect
    multi-tap sequences. The usage of immediate and/or delayed taps depend on
    the application.

    Timed gestures must be polled frequently to receive them.

    Examples:
      Resolve gesture candidates and return the highest priority gesture in the
      lifecycle's current state::

        candidates: list[GestureEvent | None] = ...
        resolver = GestureResolver()
        gesture = resolver.resolve_potential_candidates(candidates)

      Frequently poll for timed gestures::

        resolver = GestureResolver()
        timed_gesture: GestureEvent | None = None
        while True:
            timed_gesture = resolver.poll_timed_gestures()
            # Process the timed gesture here
            time.sleep(0.02)

    """

    def __init__(self) -> None:
        self._active_gesture: models.GestureEvent | None = None
        self._timed_gesture: models.GestureEvent | None = None
        self._start_time: float = 0.0

    def poll_timed_gestures(self) -> models.GestureEvent | None:
        """Poll for any timed gestures.

        Gestures that require a timer for delayed emission or further
        processing will be returned when the timer expires.

        Returns:
          The delayed gesture, or None when no delayed gesture should be
          emitted.

        """
        if self._timed_gesture is None:
            return None

        time_elapsed = time.time() - self._start_time

        if (
            self._timed_gesture.type is enums.GestureType.TAP
            and time_elapsed >= constants.GestureThreshold.BETWEEN_TAP_TIME
        ):
            delayed_tap = self._timed_gesture
            delayed_tap.type = enums.GestureType.DELAYED_TAP
            self._timed_gesture = None
            return delayed_tap

        return None

    def resolve_potential_candidates(
        self, candidates: list[models.GestureEvent | None]
    ) -> models.GestureEvent | None:
        """Return the highest priority gesture, respecting gesture lifecycle.

        A gesture lifecycle manages when a gesture is first emitted vs. when
        subsequent updates are returned. For example, HOLD gestures emit once,
        while DRAG gestures emit only when the position changes.

        The active gesture tracks the current gesture in its lifecycle. When
        a gesture with higher priority appears, it takes over. When a gesture
        ends, the active gesture is cleared.

        Args:
          candidates:
            The list of potential gestures, may contain None values.

        Returns:
          The gesture to emit, or None if no gesture should be emitted. This
          respects lifecycle rules to prevent duplicate or stale emissions.

        """
        gestures = (gesture for gesture in candidates if gesture is not None)
        gestures_by_priority = sorted(
            gestures,
            key=lambda gesture: constants.GESTURE_PRIORITY[gesture.type],
            reverse=True,
        )

        if len(gestures_by_priority) == 0:
            return None

        winner = gestures_by_priority[0]

        # Process tap gestures
        if winner.type is enums.GestureType.TAP:
            self._process_tap_candidate(winner)

        # Determine beginning or ending of lifecycle
        new_active_gesture = self._handle_gesture_lifecycle(winner)
        if new_active_gesture is not None:
            return new_active_gesture

        # Check conditions for returning the gesture
        if self._should_skip_duplicate(winner):
            return None
        if self._is_gesture_update(winner):
            self._active_gesture = winner
            return winner
        # Higher priority gestures can interrupt lower priority gestures
        if self._is_higher_priority(winner):
            self._active_gesture = winner
            return winner

        return None  # pragma: no cover

    def _process_tap_candidate(self, gesture: models.GestureEvent) -> None:
        """Count taps and detect multi-tap sequences.

        Increments tap count for consecutive taps that occur within time and
        distance thresholds. Stores the gesture as timed for delayed emission.
        """
        now = time.time()

        gesture.tap_count += 1

        # Set or replace the timed gesture
        if (
            not self._timed_gesture
            or self._timed_gesture.type is not enums.GestureType.TAP
        ):
            self._timed_gesture = gesture
            self._start_time = now
            return

        point1 = gesture.end_point
        point2 = self._timed_gesture.end_point
        duration = geometry.get_duration(point1, point2)
        distance = geometry.get_distance(point1, point2)

        if (
            duration < constants.GestureThreshold.BETWEEN_TAP_TIME
            and distance < constants.GestureThreshold.BETWEEN_TAP_DISTANCE
        ):
            gesture.tap_count = self._timed_gesture.tap_count + 1

        self._timed_gesture = gesture
        self._start_time = now

    def _handle_gesture_lifecycle(
        self, winner: models.GestureEvent
    ) -> models.GestureEvent | None:
        """Manage active gesture state.

        Clears the active gesture when a release occurs or non-lifecycle
        gestures end. Sets the active gesture on first emission of the gesture
        lifecycle.

        Args:
          winner:
            The highest priority gesture candidate.

        Returns:
          The winner gesture if it starts a new lifecycle, None if continuing
          an existing gesture.

        """
        if self._active_gesture is not None:
            winner_is_release = constants.GESTURE_IS_RELEASE[winner.type]
            active_gesture_has_lifecycle = constants.GESTURE_HAS_LIFECYCLE[
                self._active_gesture.type
            ]
            # Clear active gesture if winner is a release or active gesture
            # doesn't trigger further releases (like TAP which doesn't need a
            # release)
            if winner_is_release or not active_gesture_has_lifecycle:
                self._active_gesture = None

        # Set the beginning of the gesture lifecycle
        if self._active_gesture is None:
            self._active_gesture = winner
            return winner

        return None

    def _should_skip_duplicate(self, winner: models.GestureEvent) -> bool:
        """Check if the gesture is a duplicate of the currently active gesture.

        Prevents redundant emissions by comparing gesture type and attributes.

        Args:
          winner:
            The highest priority gesture candidate.

        Returns:
          True if the gesture duplicates the active gesture and should be
          skipped, False otherwise.

        """
        if self._active_gesture is None:  # pragma: no cover
            return False

        # Skip duplicated hold gestures
        if winner.type is self._active_gesture.type is enums.GestureType.HOLD:
            return True

        # Skip duplicated drag gestures
        if winner.type is self._active_gesture.type is enums.GestureType.DRAG:
            point1 = winner.end_point
            point2 = self._active_gesture.end_point
            # Drag is duplicate only if endpoint hasn't moved
            if point1.x == point2.x and point1.y == point2.y:
                return True

        # Skip duplicated zoom and rotate gestures
        if (
            winner.type
            is self._active_gesture.type
            is enums.GestureType.ZOOM_AND_ROTATE
        ):
            scaling1 = winner.scaling_factor
            scaling2 = self._active_gesture.scaling_factor
            rotation1 = winner.rotation_degrees
            rotation2 = self._active_gesture.rotation_degrees

            same_scale = math.isclose(scaling1, scaling2)
            same_rotation = math.isclose(rotation1, rotation2)
            # Zoom/rotate is duplicate only if scale and rotation are the same
            if same_scale and same_rotation:
                return True

        return False

    def _is_gesture_update(self, winner: models.GestureEvent) -> bool:
        """Check if the gesture is an update to the currently active gesture.

        Args:
          winner:
            The highest priority gesture candidate.

        Returns:
          True if the gesture type matches the active gesture type, False
          otherwise.

        """
        if self._active_gesture is None:  # pragma: no cover
            return False

        return winner.type is self._active_gesture.type

    def _is_higher_priority(self, winner: models.GestureEvent) -> bool:
        """Check if the gesture has higher priority than the active gesture.

        Args:
          winner:
            The highest priority gesture candidate.

        Returns:
          True if the gesture priority exceeds the active gesture priority,
          False otherwise.

        """
        if self._active_gesture is None:  # pragma: no cover
            return False

        return (
            constants.GESTURE_PRIORITY[winner.type]
            >= constants.GESTURE_PRIORITY[self._active_gesture.type]
        )
