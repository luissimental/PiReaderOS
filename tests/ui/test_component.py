import pytest
import pytest_mock

from pireaderos.ui import component


class TestComponentInitialization:
    """Test Component initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        top_level = component.Component(parent=None, width=1, height=1)

        assert isinstance(top_level.parent, component.Component | None)
        assert isinstance(top_level.children, set)
        assert isinstance(top_level._x, int)
        assert isinstance(top_level._y, int)
        assert isinstance(top_level._width, int)
        assert isinstance(top_level._height, int)
        assert top_level._scale == 1.0
        assert top_level._angle == 0.0
        assert isinstance(top_level._anchor, component.POSITIONS)

    def test_init_fails_on_invalid_width_unittest(self) -> None:
        """Raise ValueError when width is invalid."""
        with pytest.raises(ValueError):
            component.Component(parent=None, width=0, height=1)

    def test_init_fails_on_invalid_height_unittest(self) -> None:
        """Raise ValueError when height is invalid."""
        with pytest.raises(ValueError):
            component.Component(parent=None, width=1, height=0)

    def test_init_parent_is_none_for_top_level_unittest(self) -> None:
        """Parent is None for top level component."""
        top_level = component.Component(parent=None, width=1, height=1)

        assert top_level.parent is None

    def test_init_parent_is_top_level_for_child_unittest(self) -> None:
        """Parent is top level for child component."""
        top_level = component.Component(parent=None, width=1, height=1)
        child = component.Component(parent=top_level, width=1, height=1)

        assert top_level.parent is None
        assert len(top_level.children) == 1
        assert child in top_level.children

        assert child.parent is top_level
        assert len(child.children) == 0

    def test_init_parent_is_child_for_child_unittest(self) -> None:
        """Parent is another child for child component."""
        top_level = component.Component(parent=None, width=1, height=1)
        child1 = component.Component(parent=top_level, width=1, height=1)
        child2 = component.Component(parent=child1, width=1, height=1)

        assert top_level.parent is None
        assert len(top_level.children) == 1
        assert child1 in top_level.children

        assert child1.parent is top_level
        assert len(child1.children) == 1
        assert child2 in child1.children

        assert child2.parent is child1
        assert len(child2.children) == 0

    def test_init_parent_has_multiple_children_unittest(self) -> None:
        """Parent has multiple children."""
        top_level = component.Component(parent=None, width=1, height=1)
        child1 = component.Component(parent=top_level, width=1, height=1)
        child2 = component.Component(parent=top_level, width=1, height=1)

        assert top_level.parent is None
        assert len(top_level.children) == 2
        assert child1 in top_level.children
        assert child2 in top_level.children

        assert child1.parent is top_level
        assert len(child1.children) == 0

        assert child2.parent is top_level
        assert len(child2.children) == 0

    def test_init_x_is_set_unittest(self) -> None:
        """X is set after init."""
        top_level = component.Component(parent=None, x=15, width=1, height=1)

        assert top_level._x == 15

    def test_init_y_is_set_unittest(self) -> None:
        """Y is set after init."""
        top_level = component.Component(parent=None, y=15, width=1, height=1)

        assert top_level._y == 15

    def test_init_width_is_set_unittest(self) -> None:
        """Width is set after init."""
        top_level = component.Component(parent=None, width=15, height=1)

        assert top_level._width == 15

    def test_init_height_is_set_unittest(self) -> None:
        """Height is set after init."""
        top_level = component.Component(parent=None, width=1, height=15)

        assert top_level._height == 15

    @pytest.mark.parametrize(
        "position, expected_anchor",
        [
            (
                component.POSITIONS.NOOP,
                component.POSITIONS.TOP | component.POSITIONS.LEFT,
            ),
            (component.POSITIONS.LEFT, component.POSITIONS.LEFT),
            (component.POSITIONS.RIGHT, component.POSITIONS.RIGHT),
            (
                component.POSITIONS.TOP | component.POSITIONS.RIGHT,
                component.POSITIONS.TOP | component.POSITIONS.RIGHT,
            ),
        ],
    )
    def test_init_anchor_is_set_unittest(
        self,
        position: component.POSITIONS,
        expected_anchor: component.POSITIONS,
    ) -> None:
        """Anchor is set after init."""
        top_level = component.Component(
            parent=None, width=1, height=1, anchor=position
        )

        assert top_level._anchor is expected_anchor

    def test_anchor_is_set_as_top_left_when_omitted_unittest(self) -> None:
        """Anchor is set as TOP LEFT after init when omitted."""
        top_level = component.Component(parent=None, width=1, height=1)

        assert (
            top_level._anchor
            is component.POSITIONS.TOP | component.POSITIONS.LEFT
        )


class TestComponentFullScreen:
    """Test Component full_screen."""

    def test_full_screen_component_has_attributes_unittest(self) -> None:
        """Full screen component has proper attributes."""
        top_level = component.Component.full_screen(
            parent=None, anchor=component.POSITIONS.LEFT
        )

        assert top_level.parent is None
        assert len(top_level.children) == 0
        assert top_level._x == 0
        assert top_level._y == 0
        assert top_level._width == component.DIMENSIONS.WIDTH
        assert top_level._height == component.DIMENSIONS.HEIGHT
        assert top_level._scale == 1.0
        assert top_level._angle == 0.0
        assert top_level._anchor is component.POSITIONS.LEFT


class TestComponentXProperty:
    """Test Component x property."""

    @pytest.mark.parametrize(
        "position, expected_x",
        [
            (component.POSITIONS.TOP | component.POSITIONS.LEFT, 2 + 3),
            (component.POSITIONS.TOP | component.POSITIONS.MIDDLE, 2 + 3 - 3),
            (component.POSITIONS.TOP | component.POSITIONS.RIGHT, 2 + 3 - 6),
            (component.POSITIONS.NOOP | component.POSITIONS.RIGHT, 2 + 3 - 6),
        ],
    )
    def test_x_gets_absolute_x_on_anchor_unittest(
        self, position: component.POSITIONS, expected_x: int
    ) -> None:
        """X gets absolute x value based on anchor."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level,
            x=3,
            y=4,
            width=6,
            height=8,
            anchor=position,
        )

        assert top_level.x == 2
        assert child.x == expected_x

    @pytest.mark.parametrize(
        "position",
        [
            component.POSITIONS.LEFT,
            component.POSITIONS.MIDDLE,
            component.POSITIONS.RIGHT,
        ],
    )
    def test_x_sets_absolute_x_unittest(
        self, position: component.POSITIONS
    ) -> None:
        """X sets the absolute x value."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level, x=3, y=4, width=6, height=8, anchor=position
        )

        child.x += 100

        # Relative position is expected to not depend on anchor
        assert child._x == 103


class TestComponentXRelProperty:
    """Test Component x_rel property."""

    def test_x_rel_gets_relative_x_unittest(self) -> None:
        """X_rel gets x position relative to parent."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level, x=3, y=4, width=6, height=8
        )

        assert top_level.x_rel == 2
        assert child.x_rel == 3

    def test_x_rel_sets_relative_x_unittest(self) -> None:
        """X_rel sets x position relative to parent."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level, x=3, y=4, width=6, height=8
        )

        top_level.x_rel = 5
        child.x_rel = 6

        assert top_level._x == 5
        assert child._x == 6


class TestComponentYProperty:
    """Test Component y property."""

    @pytest.mark.parametrize(
        "position, expected_y",
        [
            (component.POSITIONS.LEFT | component.POSITIONS.TOP, 4 + 5),
            (component.POSITIONS.LEFT | component.POSITIONS.MIDDLE, 4 + 5 - 4),
            (component.POSITIONS.LEFT | component.POSITIONS.BOTTOM, 4 + 5 - 8),
            (component.POSITIONS.NOOP | component.POSITIONS.BOTTOM, 4 + 5 - 8),
        ],
    )
    def test_y_gets_absolute_y_on_anchor_unittest(
        self, position: component.POSITIONS, expected_y: int
    ) -> None:
        """Y gets absolute y value based on anchor."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level,
            x=2,
            y=5,
            width=6,
            height=8,
            anchor=position,
        )

        assert top_level.y == 4
        assert child.y == expected_y

    @pytest.mark.parametrize(
        "position",
        [
            component.POSITIONS.TOP,
            component.POSITIONS.MIDDLE,
            component.POSITIONS.BOTTOM,
        ],
    )
    def test_y_sets_absolute_y_unittest(
        self, position: component.POSITIONS
    ) -> None:
        """X sets the absolute x value."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level, x=3, y=4, width=6, height=8, anchor=position
        )

        child.y += 100

        # Relative position is expected to not depend on anchor
        assert child._y == 104


class TestComponentYRelProperty:
    """Test Component y_rel property."""

    def test_y_rel_gets_relative_y_unittest(self) -> None:
        """Y_rel gets y position relative to parent."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level, x=2, y=5, width=6, height=8
        )

        assert top_level.y_rel == 4
        assert child.y_rel == 5

    def test_y_rel_sets_relative_y_unittest(self) -> None:
        """Y_rel sets y position relative to parent."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level, x=2, y=5, width=6, height=8
        )

        top_level.y_rel = 10
        child.y_rel = 11

        assert top_level._y == 10
        assert child._y == 11


class TestComponentAnchorProperty:
    """Test Component anchor property."""

    @pytest.mark.parametrize(
        "position, expected_anchor",
        [
            (component.POSITIONS.TOP, component.POSITIONS.TOP),
            (component.POSITIONS.MIDDLE, component.POSITIONS.MIDDLE),
            (
                component.POSITIONS.TOP | component.POSITIONS.MIDDLE,
                component.POSITIONS.TOP | component.POSITIONS.MIDDLE,
            ),
            (
                component.POSITIONS.NOOP,
                component.POSITIONS.TOP | component.POSITIONS.LEFT,
            ),
        ],
    )
    def test_anchor_gets_component_anchor_unittest(
        self,
        position: component.POSITIONS,
        expected_anchor: component.POSITIONS,
    ) -> None:
        """Anchor gets the component anchor."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8, anchor=position
        )

        assert top_level.anchor is expected_anchor

    @pytest.mark.parametrize(
        "position, expected_anchor",
        [
            (component.POSITIONS.TOP, component.POSITIONS.TOP),
            (component.POSITIONS.MIDDLE, component.POSITIONS.MIDDLE),
            (
                component.POSITIONS.TOP | component.POSITIONS.MIDDLE,
                component.POSITIONS.TOP | component.POSITIONS.MIDDLE,
            ),
            (
                component.POSITIONS.NOOP,
                component.POSITIONS.TOP | component.POSITIONS.LEFT,
            ),
        ],
    )
    def test_anchor_sets_component_anchor_unittest(
        self,
        position: component.POSITIONS,
        expected_anchor: component.POSITIONS,
    ) -> None:
        """Anchor sets the component anchor."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )

        top_level.anchor = position

        assert top_level._anchor is expected_anchor


class TestComponentAddChild:
    """Test Component add_child."""

    def test_add_does_not_work_when_component_is_self_unittest(self) -> None:
        """Return immediately when attempting to add itself."""
        top_level = component.Component.full_screen(parent=None)
        child = component.Component.full_screen(parent=top_level)

        child.add_child(child)

        assert top_level.parent is None
        assert len(top_level.children) == 1
        assert child in top_level.children

        assert child.parent is top_level
        assert len(child.children) == 0

    def test_add_child_already_has_a_parent_unittest(self) -> None:
        """Remove from parent's children then add new parent."""
        top_level = component.Component.full_screen(parent=None)
        child1 = component.Component.full_screen(parent=top_level)
        grandchild = component.Component.full_screen(parent=child1)
        child2 = component.Component.full_screen(parent=top_level)

        child2.add_child(grandchild)

        assert top_level.parent is None
        assert len(top_level.children) == 2
        assert child1 in top_level.children
        assert child2 in top_level.children

        assert child1.parent is top_level
        assert len(child1.children) == 0

        assert child2.parent is top_level
        assert len(child2.children) == 1
        assert grandchild in child2.children

        assert grandchild.parent is child2
        assert len(grandchild.children) == 0

    def test_add_child_has_no_parent_unittest(self) -> None:
        """Add child that has no parent."""
        top_level = component.Component.full_screen(parent=None)
        child1 = component.Component.full_screen(parent=None)

        top_level.add_child(child1)

        assert top_level.parent is None
        assert len(top_level.children) == 1
        assert child1 in top_level.children

        assert child1.parent is top_level
        assert len(child1.children) == 0


class TestComponentRemoveChild:
    """Test Component remove_child."""

    def test_remove_child_unittest(self) -> None:
        """Remove child successfully."""
        top_level = component.Component.full_screen(parent=None)
        child1 = component.Component.full_screen(parent=top_level)

        top_level.remove_child(child1)

        assert top_level.parent is None
        assert len(top_level.children) == 0

        assert child1.parent is None
        assert len(child1.children) == 0

    def test_remove_child_wrong_parent_unittest(self) -> None:
        """No removals occur when parent is not self."""
        top_level = component.Component.full_screen(parent=None)
        child1 = component.Component.full_screen(parent=top_level)

        child1.remove_child(child1)

        assert top_level.parent is None
        assert len(top_level.children) == 1
        assert child1 in top_level.children

        assert child1.parent is top_level
        assert len(child1.children) == 0


class TestComponentSnapTo:
    """Test Component snap_to."""

    @pytest.mark.parametrize(
        "position, expected_x, expected_y",
        [
            (component.POSITIONS.NOOP, 2, 4),
            (component.POSITIONS.LEFT, 0, 4),
            (component.POSITIONS.MIDDLE, 500, 2000),
            (component.POSITIONS.RIGHT, 1000, 4),
            (component.POSITIONS.TOP, 2, 0),
            (component.POSITIONS.BOTTOM, 2, 4000),
            (component.POSITIONS.BOTTOM | component.POSITIONS.NOOP, 2, 4000),
        ],
    )
    def test_snap_one_position_top_level_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        position: component.POSITIONS,
        expected_x: int,
        expected_y: int,
    ) -> None:
        """Snap has one position for top level component."""
        mocker.patch.object(component.DIMENSIONS, "WIDTH", 1000)
        mocker.patch.object(component.DIMENSIONS, "HEIGHT", 4000)
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )

        top_level.snap_to(position)

        assert top_level._x == expected_x
        assert top_level._y == expected_y

    @pytest.mark.parametrize(
        "position1, position2, expected_x, expected_y",
        [
            (component.POSITIONS.TOP, component.POSITIONS.LEFT, 0, 0),
            (component.POSITIONS.TOP, component.POSITIONS.MIDDLE, 50, 0),
            (component.POSITIONS.TOP, component.POSITIONS.RIGHT, 100, 0),
            (component.POSITIONS.MIDDLE, component.POSITIONS.RIGHT, 100, 5),
            (component.POSITIONS.BOTTOM, component.POSITIONS.RIGHT, 100, 10),
            (component.POSITIONS.MIDDLE, component.POSITIONS.BOTTOM, 50, 10),
            (component.POSITIONS.LEFT, component.POSITIONS.BOTTOM, 0, 10),
            (component.POSITIONS.MIDDLE, component.POSITIONS.LEFT, 0, 5),
            (
                component.POSITIONS.NOOP | component.POSITIONS.MIDDLE,
                component.POSITIONS.LEFT,
                0,
                5,
            ),
        ],
    )
    def test_snap_two_positions_top_level_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        position1: component.POSITIONS,
        position2: component.POSITIONS,
        expected_x: int,
        expected_y: int,
    ) -> None:
        """Snap has two positions for top level component."""
        mocker.patch.object(component.DIMENSIONS, "WIDTH", 100)
        mocker.patch.object(component.DIMENSIONS, "HEIGHT", 10)
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )

        top_level.snap_to(position1 | position2)

        assert top_level._x == expected_x
        assert top_level._y == expected_y

    @pytest.mark.parametrize(
        "position, expected_x, expected_y",
        [
            (component.POSITIONS.NOOP, 2, 4),
            (component.POSITIONS.LEFT, 0, 4),
            (component.POSITIONS.MIDDLE, 500, 2000),
            (component.POSITIONS.RIGHT, 1000, 4),
            (component.POSITIONS.TOP, 2, 0),
            (component.POSITIONS.BOTTOM, 2, 4000),
            (component.POSITIONS.BOTTOM | component.POSITIONS.NOOP, 2, 4000),
        ],
    )
    def test_snap_one_position_child_unittest(
        self, position: component.POSITIONS, expected_x: int, expected_y: int
    ) -> None:
        """Snap has one position for child component."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=1000, height=4000
        )
        child = component.Component(
            parent=top_level, x=2, y=4, width=6, height=8
        )

        child.snap_to(position)

        assert child._x == expected_x
        assert child._y == expected_y

    @pytest.mark.parametrize(
        "position1, position2, expected_x, expected_y",
        [
            (component.POSITIONS.TOP, component.POSITIONS.LEFT, 0, 0),
            (component.POSITIONS.TOP, component.POSITIONS.MIDDLE, 50, 0),
            (component.POSITIONS.TOP, component.POSITIONS.RIGHT, 100, 0),
            (component.POSITIONS.MIDDLE, component.POSITIONS.RIGHT, 100, 5),
            (component.POSITIONS.BOTTOM, component.POSITIONS.RIGHT, 100, 10),
            (component.POSITIONS.MIDDLE, component.POSITIONS.BOTTOM, 50, 10),
            (component.POSITIONS.LEFT, component.POSITIONS.BOTTOM, 0, 10),
            (component.POSITIONS.MIDDLE, component.POSITIONS.LEFT, 0, 5),
            (
                component.POSITIONS.MIDDLE | component.POSITIONS.NOOP,
                component.POSITIONS.LEFT,
                0,
                5,
            ),
        ],
    )
    def test_snap_two_positions_child_unittest(
        self,
        position1: component.POSITIONS,
        position2: component.POSITIONS,
        expected_x: int,
        expected_y: int,
    ) -> None:
        """Snap has two positions for child component."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=100, height=10
        )
        child = component.Component(
            parent=top_level, x=2, y=4, width=6, height=8
        )

        child.snap_to(position1 | position2)

        assert child._x == expected_x
        assert child._y == expected_y


class TestRemoveComponent:
    """Test remove_component."""

    def test_remove_top_level_returns_immediately_unittest(self) -> None:
        """Remove top level component returns immediately."""
        top_level = component.Component.full_screen(parent=None)
        child1 = component.Component.full_screen(parent=top_level)
        child2 = component.Component.full_screen(parent=top_level)

        component.remove_component(top_level)

        assert top_level.parent is None
        assert len(top_level.children) == 2
        assert child1 in top_level.children
        assert child2 in top_level.children

        assert child1.parent is top_level
        assert len(child1.children) == 0

        assert child2.parent is top_level
        assert len(child2.children) == 0

    def test_remove_component_has_no_children_unittest(self) -> None:
        """Remove component that has no children."""
        top_level = component.Component.full_screen(parent=None)
        child1 = component.Component.full_screen(parent=top_level)
        child2 = component.Component.full_screen(parent=top_level)

        component.remove_component(child1)

        assert top_level.parent is None
        assert len(top_level.children) == 1
        assert child1 not in top_level.children
        assert child2 in top_level.children

        assert child1.parent is None
        assert len(child1.children) == 0

        assert child2.parent is top_level
        assert len(child2.children) == 0

    def test_remove_component_has_multiple_children_unittest(self) -> None:
        """Remove component with multiple children."""
        top_level = component.Component.full_screen(parent=None)
        child1 = component.Component.full_screen(parent=top_level)
        grandchild1 = component.Component.full_screen(parent=child1)
        grandchild2 = component.Component.full_screen(parent=child1)
        child2 = component.Component.full_screen(parent=top_level)

        component.remove_component(child1)

        assert top_level.parent is None
        assert len(top_level.children) == 3
        assert child1 not in top_level.children
        assert grandchild1 in top_level.children
        assert grandchild2 in top_level.children
        assert child2 in top_level.children

        assert child1.parent is None
        assert len(child1.children) == 0

        assert grandchild1.parent is top_level
        assert len(grandchild1.children) == 0

        assert grandchild2.parent is top_level
        assert len(grandchild2.children) == 0

        assert child2.parent is top_level
        assert len(child2.children) == 0


class TestRemoveBranch:
    """Test remove_branch."""

    def test_remove_top_level_descendants_unittest(self) -> None:
        """Remove top level descendants."""
        top_level = component.Component.full_screen(parent=None)
        child1 = component.Component.full_screen(parent=top_level)
        grandchild1 = component.Component.full_screen(parent=child1)
        grandchild2 = component.Component.full_screen(parent=child1)
        child2 = component.Component.full_screen(parent=top_level)

        component.remove_branch(top_level)

        assert top_level.parent is None
        assert len(top_level.children) == 0

        assert child1.parent is None
        assert len(child1.children) == 0

        assert grandchild1.parent is None
        assert len(grandchild1.children) == 0

        assert grandchild2.parent is None
        assert len(grandchild2.children) == 0

        assert child2.parent is None
        assert len(child2.children) == 0

    def test_remove_component_descendants_unittest(self) -> None:
        """Remove component descendants."""
        top_level = component.Component.full_screen(parent=None)
        child1 = component.Component.full_screen(parent=top_level)
        grandchild1 = component.Component.full_screen(parent=child1)
        grandchild2 = component.Component.full_screen(parent=child1)
        child2 = component.Component.full_screen(parent=top_level)
        grandchild3 = component.Component.full_screen(parent=child2)

        component.remove_branch(child1)

        assert top_level.parent is None
        assert len(top_level.children) == 1
        assert child2 in top_level.children

        assert child1.parent is None
        assert len(child1.children) == 0

        assert grandchild1.parent is None
        assert len(grandchild1.children) == 0

        assert grandchild2.parent is None
        assert len(grandchild2.children) == 0

        assert child2.parent is top_level
        assert len(child2.children) == 1
        assert grandchild3 in child2.children

        assert grandchild3.parent is child2
        assert len(grandchild3.children) == 0
