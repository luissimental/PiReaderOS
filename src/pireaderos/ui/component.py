from __future__ import annotations

import enum
from typing import Self


class DIMENSIONS:
    """The screen dimensions of the e-paper display."""

    WIDTH = 480
    HEIGHT = 800


class POSITIONS(enum.Flag):
    """The predefined component positions.

    Two positions can be combined to create position combinations. For example,
    `TOP | LEFT` refers to the TOP LEFT of the component.

    `NOOP` by itself represents a default state depending on the API, however,
    its presence with other positions can be simply ignored. For example,
    `NOOP | TOP | LEFT` is equivalent to `TOP | LEFT`.

    Unconventional combinations such as `LEFT | RIGHT` or `TOP | BOTTOM` may
    result in undefined behavior.

    Attributes:
      NOOP:
        Do nothing (no-op).
      TOP:
        The TOP position of the component.
      BOTTOM:
        The BOTTOM position of the component.
      MIDDLE:
        The MIDDLE position of the component.
      LEFT:
        The LEFT position of the component.
      RIGHT:
        The RIGHT position of the component.

    """

    NOOP = enum.auto()
    TOP = enum.auto()
    BOTTOM = enum.auto()
    MIDDLE = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()


class Component:
    def __init__(
        self,
        *,
        parent: Component | None,
        x: int = 0,
        y: int = 0,
        width: int,
        height: int,
        anchor: POSITIONS = POSITIONS.TOP | POSITIONS.LEFT,
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
        self.children: set[Component] = set()

        if parent is not None:
            self.parent = parent
            parent.children.add(self)

        self._x = x  # stores x relative to the parent
        self._y = y  # stores y relative to the parent
        self._width = width
        self._height = height
        self._scale = 1.0
        self._angle = 0.0

        if anchor is POSITIONS.NOOP:
            self._anchor = POSITIONS.TOP | POSITIONS.LEFT
        else:
            self._anchor = anchor

    @classmethod
    def full_screen(
        cls,
        parent: Component | None,
        anchor: POSITIONS = POSITIONS.TOP | POSITIONS.LEFT,
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
            width=DIMENSIONS.WIDTH,
            height=DIMENSIONS.HEIGHT,
            anchor=anchor,
        )

    @property
    def x(self) -> int:
        """The component's absolute x position. Depends on the anchor."""
        parent_x = 0 if self.parent is None else self.parent.x  # recursive x
        abs_x = self._x + parent_x  # left position (default)

        if POSITIONS.MIDDLE in self._anchor:
            abs_x -= self._width // 2
        elif POSITIONS.RIGHT in self._anchor:
            abs_x -= self._width

        return abs_x

    @x.setter
    def x(self, x: int) -> None:
        # Add the difference since self._x is a relative position and x is an
        # absolute position
        self._x += x - self.x

    @property
    def x_rel(self) -> int:
        """The component's x position relative to the parent."""
        return self._x

    @x_rel.setter
    def x_rel(self, x_rel: int) -> None:
        self._x = x_rel

    @property
    def y(self) -> int:
        """The component's absolute y position. Depends on the anchor."""
        parent_y = 0 if self.parent is None else self.parent.y  # recursive y
        abs_y = self._y + parent_y  # top position (default)

        if POSITIONS.MIDDLE in self._anchor:
            abs_y -= self._height // 2
        elif POSITIONS.BOTTOM in self._anchor:
            abs_y -= self._height

        return abs_y

    @y.setter
    def y(self, y: int) -> None:
        # Add the difference since self._y is a relative position and y is an
        # absolute position
        self._y += y - self.y

    @property
    def y_rel(self) -> int:
        """The component's y position relative to the parent."""
        return self._y

    @y_rel.setter
    def y_rel(self, y_rel: int) -> None:
        self._y = y_rel

    @property
    def anchor(self) -> POSITIONS:
        """The anchor of the component.

        Used for aligning the x and y coordinates. `NOOP` defaults to TOP LEFT
        of the component.
        """
        return self._anchor

    @anchor.setter
    def anchor(self, anchor: POSITIONS) -> None:
        if anchor is POSITIONS.NOOP:
            self._anchor = POSITIONS.TOP | POSITIONS.LEFT
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

        self.children.add(component)
        component.parent = self

    def remove_child(self, component: Component) -> None:
        """Remove a child component.

        If the child component's parent is not self, then no removals occur.
        The child component's descendants are preserved.
        """
        if component.parent is self:
            self.children.discard(component)
            component.parent = None

    def snap_to(self, position: POSITIONS) -> None:
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
        if position is POSITIONS.NOOP:
            return

        snap_x = self._x
        snap_y = self._y

        if self.parent is None:
            parent_width = DIMENSIONS.WIDTH
            parent_height = DIMENSIONS.HEIGHT
        else:
            parent_width = self.parent._width
            parent_height = self.parent._height

        if POSITIONS.MIDDLE in position:
            snap_x = parent_width // 2
            snap_y = parent_height // 2

        if POSITIONS.LEFT in position:
            snap_x = 0
        elif POSITIONS.RIGHT in position:
            snap_x = parent_width

        if POSITIONS.TOP in position:
            snap_y = 0
        elif POSITIONS.BOTTOM in position:
            snap_y = parent_height

        self._x = snap_x
        self._y = snap_y


def remove_component(component: Component) -> None:
    """Remove a component from the tree and reassign children.

    If the component is the top level component, the function returns
    immediately.
    """
    if component.parent is None:
        return

    component.parent.children.discard(component)
    component.parent.children.update(component.children)

    for children in component.children:
        children.parent = component.parent

    component.parent = None
    component.children.clear()


def remove_branch(component: Component) -> None:
    """Remove a component and all of its descendants."""
    if component.parent is not None:
        component.parent.children.discard(component)
        component.parent = None

    stack = [component]
    while stack:
        current = stack.pop()
        for child in current.children:
            child.parent = None
            stack.append(child)
        current.children.clear()
