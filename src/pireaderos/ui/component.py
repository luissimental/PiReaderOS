from __future__ import annotations

import math
from typing import TYPE_CHECKING, Self

from pireaderos.common import constants, enums, matrix

if TYPE_CHECKING:
    from pireaderos.common import models
    from pireaderos.ui.behavior import base


class Component:
    """Base class for UI elements within a hierarchical component system.

    Coordinates a parent-child tree structure where children are stored in a
    list to maintain rendering order (Z-order). Components at the end of the
    list are rendered last, appearing on top of earlier components.

    Gesture Handling:
      Gestures are dispatched from top to bottom (reverse rendering order). The
      first component to intersect the touch point consumes the event,
      preventing 'click-through' to elements positioned underneath. Low level
      gesture handling is offered by activating specific behaviors.

    Attributes:
      parent:
        The containing component. Defaults to None.
      children:
        A list of child components, ordered from bottom (index 0) to top
        (index -1) visually.

    """

    def __init__(
        self,
        *,
        parent: Component | None,
        x: int = 0,
        y: int = 0,
        width: int,
        height: int,
        anchor: enums.Position = enums.Position.TOP | enums.Position.LEFT,
    ) -> None:
        """Initialize the component.

        Args:
          parent:
            The parent component. The only component initialized with
            `parent` as `None` is the top level component in the hierarchy. All
            other components are children, thus, `parent` must not be None
            after defining the top level component. The top level component's
            `parent` is set to itself.
          x:
            The initial x position relative to the parent. Depends on the
            anchor.
          y:
            The initial y position relative to the parent. Depends on the
            anchor.
          width:
            The width of the component. Must be greater than 0.
          height:
            The height of the component. Must be greater than 0.
          anchor:
            The anchor of the component used for aligning the x and y
            coordinates. `NOOP` defaults to TOP LEFT of the component.

        """
        msg = ""
        if width <= 0:
            msg = "width must be greater than 0."
        if height <= 0:
            msg = "height must be greater than 0."
        if msg:
            raise ValueError(msg)

        self.parent: Component | None = None
        self.children: list[Component] = []

        if parent is not None:
            self.parent = parent
            parent.children.append(self)

        self._x = x  # stores x relative to the parent
        self._y = y  # stores y relative to the parent
        self._width = width
        self._height = height
        self._scale = 1.0
        self._angle = 0.0

        if anchor is enums.Position.NOOP:
            self._anchor = enums.Position.TOP | enums.Position.LEFT
        else:
            self._anchor = anchor

        # Flag for detecting changes in x, y, scale, or angle
        self._matrix_dirty: bool = True
        # Cache matrices to speed up computation
        self._local_matrix: matrix.AffineMatrix2D | None = None
        self._world_matrix: matrix.AffineMatrix2D | None = None

        self._behaviors: set[base.BaseBehavior] = set()

    @classmethod
    def full_screen(
        cls,
        parent: Component | None,
        anchor: enums.Position = enums.Position.TOP | enums.Position.LEFT,
    ) -> Self:
        """Create a component with full screen attributes.

        Args:
          parent:
            The parent component. The only component initialized with
            `parent` as `None` is the top level component in the hierarchy. All
            other components are children, thus, `parent` must not be None
            after defining the top level component. The top level component's
            `parent` is set to itself.
          anchor:
            The anchor of the component used for aligning the x and y
            coordinates. `NOOP` defaults to TOP LEFT of the component.

        Returns:
          The full screen component object.

        """
        return cls(
            parent=parent,
            width=constants.Dimensions.WIDTH,
            height=constants.Dimensions.HEIGHT,
            anchor=anchor,
        )

    @property
    def screen_space(self) -> tuple[int, int]:
        """The screen space (x, y) of the component's top left corner."""
        world_matrix = self._get_world_matrix()

        abs_x, abs_y = world_matrix.transform_point(0, 0)
        return int(abs_x), int(abs_y)

    @property
    def x(self) -> int:
        """The absolute x coordinate of the top-left corner.

        The anchor of the component is taken into account.
        """
        return self.screen_space[0]

    @x.setter
    def x(self, x: int) -> None:
        prev_x = self._x
        # Add the difference since self._x is a relative position and x is an
        # absolute position
        self._x += x - self.x

        if self._x != prev_x:
            self._invalidate_transform()

    @property
    def x_rel(self) -> int:
        """The component's x position relative to the parent."""
        return self._x

    @x_rel.setter
    def x_rel(self, x_rel: int) -> None:
        if self._x != x_rel:
            self._x = x_rel
            self._invalidate_transform()

    @property
    def y(self) -> int:
        """The absolute y coordinate of the top-left corner.

        The anchor of the component is taken into account.
        """
        return self.screen_space[1]

    @y.setter
    def y(self, y: int) -> None:
        prev_y = self._y
        # Add the difference since self._y is a relative position and y is an
        # absolute position
        self._y += y - self.y

        if self._y != prev_y:
            self._invalidate_transform()

    @property
    def y_rel(self) -> int:
        """The component's y position relative to the parent."""
        return self._y

    @y_rel.setter
    def y_rel(self, y_rel: int) -> None:
        if self._y != y_rel:
            self._y = y_rel
            self._invalidate_transform()

    @property
    def scale(self) -> float:
        """The component's scale factor."""
        return self._scale

    @scale.setter
    def scale(self, scale: float) -> None:
        if self._scale != scale:
            self._scale = scale
            self._invalidate_transform()

    @property
    def angle(self) -> float:
        """The component's angle in degrees."""
        return self._angle

    @angle.setter
    def angle(self, angle: float) -> None:
        if self._angle != angle:
            self._angle = angle
            self._invalidate_transform()

    @property
    def anchor(self) -> enums.Position:
        """The anchor of the component.

        Used for aligning the x and y coordinates. `NOOP` defaults to TOP LEFT
        of the component.
        """
        return self._anchor

    @anchor.setter
    def anchor(self, anchor: enums.Position) -> None:
        if anchor is enums.Position.NOOP:
            self._anchor = enums.Position.TOP | enums.Position.LEFT
        else:
            self._anchor = anchor

    def add_child(self, component: Component) -> None:
        """Add a child component.

        If the component already has a parent, the component is removed from
        the parent's children and assigned to the new parent.
        """
        if component is self:
            return

        if component.parent is not None:
            component.parent.remove_child(component)

        self.children.append(component)
        component.parent = self

    def remove_child(self, component: Component) -> None:
        """Remove a child component.

        If the child component's parent is not self, then no removals occur.
        The child component's descendants are preserved.
        """
        if component.parent is self:
            self.children.remove(component)
            component.parent = None

    def add_behavior(self, behavior: base.BaseBehavior) -> None:
        """Add a behavior to the component.

        If behavior type is already present, replace it with the new behavior.
        """
        present_behavior = self.get_behavior(type(behavior))
        if present_behavior is not None:
            self._behaviors.discard(present_behavior)

        self._behaviors.add(behavior)

    def get_behavior(
        self, behavior_class: type[base.BaseBehavior]
    ) -> base.BaseBehavior | None:
        """Get the behavior instance from the behavior class if present."""
        for behavior in self._behaviors:
            if isinstance(behavior, behavior_class):
                return behavior

        return None

    def remove_behavior(self, behavior: base.BaseBehavior) -> None:
        """Remove a behavior from the component if present."""
        self._behaviors.discard(behavior)

    def remove_behaviors(self) -> None:
        """Remove all behaviors from the component."""
        self._behaviors.clear()

    def activate_behavior(
        self, behavior: base.BaseBehavior, gesture: models.GestureEvent
    ) -> None:
        """Pass a gesture to a behavior if present."""
        if behavior in self._behaviors:
            behavior.handle_gesture(self, gesture)

    def activate_behaviors(self, gesture: models.GestureEvent) -> None:
        """Pass a gesture to all behaviors."""
        for behavior in self._behaviors:
            behavior.handle_gesture(self, gesture)

    def dispatch_gesture(
        self, gesture: models.GestureEvent
    ) -> Component | None:
        """Traverse the tree from the component to dispatch a gesture.

        Returns:
          The component that handled the gesture. May be None if no component
          handled the gesture.

        """
        if enums.GESTURE_IS_SINGLE_TOUCH[gesture.type]:
            point = gesture.end_point
        else:
            point = gesture.mid_point

        if point is None:  # pragma: no cover
            return None

        # Check children first (top to bottom)
        for child in reversed(self.children):
            if child.dispatch_gesture(gesture) is not None:
                return child

        # Dispatch gesture to all behaviors
        if self.was_touched(point.x, point.y):
            self.activate_behaviors(gesture)
            return self

        return None

    def snap_to(self, position: enums.Position) -> None:
        """Snap the component's x and y relative to the parent.

        Snapping the component's position depends on its anchor.

        Args:
          position:
            The position to snap the component. One or two positions can be
            used at the same time. For example, `TOP | LEFT` snaps the
            component TOP LEFT of the parent. `NOOP` by itself returns
            immediately, however, its presence with other positions is simply
            ignored and runs normally.

        """
        if position is enums.Position.NOOP:
            return

        snap_x = self._x
        snap_y = self._y

        if self.parent is None:
            parent_width = constants.Dimensions.WIDTH
            parent_height = constants.Dimensions.HEIGHT
        else:
            parent_width = self.parent._width
            parent_height = self.parent._height

        if enums.Position.MIDDLE in position:
            snap_x = parent_width // 2
            snap_y = parent_height // 2

        if enums.Position.LEFT in position:
            snap_x = 0
        elif enums.Position.RIGHT in position:
            snap_x = parent_width

        if enums.Position.TOP in position:
            snap_y = 0
        elif enums.Position.BOTTOM in position:
            snap_y = parent_height

        self._x = snap_x
        self._y = snap_y

    def was_touched(self, absolute_x: int, absolute_y: int) -> bool:
        """Check if absolute x and y fall within component boundaries."""
        # Inverse the world matrix to transform screen space into local space
        world_matrix = self._get_world_matrix()
        inverse_matrix = world_matrix.inverse()

        rel_x, rel_y = inverse_matrix.transform_point(absolute_x, absolute_y)
        return 0 <= rel_x <= self._width and 0 <= rel_y <= self._height

    def _invalidate_transform(self) -> None:
        """Recursively mark self and all children as needing matrix update."""
        if self._matrix_dirty:
            return

        self._matrix_dirty = True
        for child in self.children:
            child._invalidate_transform()

    def _get_anchor_offsets(self) -> tuple[float, float]:
        """Return the (x, y) pixels to shift based on the anchor."""
        off_x = 0.0
        off_y = 0.0

        if enums.Position.MIDDLE in self._anchor:
            off_x = self._width / 2
            off_y = self._height / 2

        if enums.Position.LEFT in self._anchor:
            off_x = 0.0
        elif enums.Position.RIGHT in self._anchor:
            off_x = self._width

        if enums.Position.TOP in self._anchor:
            off_y = 0.0
        elif enums.Position.BOTTOM in self._anchor:
            off_y = self._height

        return off_x, off_y

    def _get_local_matrix(self) -> matrix.AffineMatrix2D:
        """Compute matrix from x, y, scale, and angle. Depends on anchor."""
        if self._matrix_dirty or self._local_matrix is None:
            rad = math.radians(self._angle)
            cos_a = math.cos(rad) * self._scale
            sin_a = math.sin(rad) * self._scale

            ox, oy = self._get_anchor_offsets()

            # 1. Translate to position
            # 2. Rotate and scale
            # 3. Translate by anchor (rotation happens around anchor)
            tx = self._x - (ox * cos_a - oy * sin_a)
            ty = self._y - (ox * sin_a + oy * cos_a)

            # Standard Affine Matrix:
            # [ cos*s, -sin*s, tx ]  # noqa: ERA001
            # [ sin*s,  cos*s, ty ]  # noqa: ERA001
            local = matrix.AffineMatrix2D(cos_a, sin_a, -sin_a, cos_a, tx, ty)
            self._local_matrix = local

            self._matrix_dirty = False

        return self._local_matrix

    def _get_world_matrix(self) -> matrix.AffineMatrix2D:
        """Compute world matrix up the tree to the top level component."""
        if self._matrix_dirty or self._world_matrix is None:
            local = self._get_local_matrix()

            if self.parent is None:
                self._world_matrix = local
            else:
                parent_world_matrix = self.parent._get_world_matrix()
                self._world_matrix = parent_world_matrix.multiply(local)

            self._matrix_dirty = False

        return self._world_matrix


def remove_component(component: Component) -> None:
    """Remove a component from the tree and reassign children.

    If the component is the top level component, the function returns
    immediately.
    """
    if component.parent is None:
        return

    component.parent.children.remove(component)
    component.parent.children.extend(component.children)

    for children in component.children:
        children.parent = component.parent

    component.parent = None
    component.children.clear()


def remove_branch(component: Component) -> None:
    """Remove a component and all of its descendants."""
    if component.parent is not None:
        component.parent.children.remove(component)
        component.parent = None

    stack = [component]
    while stack:
        current = stack.pop()
        for child in current.children:
            child.parent = None
            stack.append(child)
        current.children.clear()
