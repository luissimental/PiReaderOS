import math

import pytest
import pytest_mock

from pireaderos.common import constants, enums, matrix, models
from pireaderos.ui import component
from pireaderos.ui.behavior import drag, hold


def create_gesture() -> models.GestureEvent:
    """Create a GestureEvent."""
    return models.GestureEvent(
        type=enums.GestureType.HOLD,
        start_point=models.TouchPoint(0, 0, 0, 0),
        end_point=models.TouchPoint(0, 0, 0, 0),
        mid_point=models.TouchPoint(0, 0, 0, 0),
    )


class TestComponentInitialization:
    """Test Component initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        top_level = component.Component(parent=None, width=1, height=1)

        assert isinstance(top_level.parent, component.Component | None)
        assert isinstance(top_level.children, list)
        assert isinstance(top_level._x, int)
        assert isinstance(top_level._y, int)
        assert isinstance(top_level._width, int)
        assert isinstance(top_level._height, int)
        assert top_level._scale == 1.0
        assert top_level._angle == 0.0
        assert isinstance(top_level._anchor, enums.Position)
        assert top_level._matrix_dirty
        assert isinstance(
            top_level._local_matrix, matrix.AffineMatrix2D | None
        )
        assert isinstance(
            top_level._world_matrix, matrix.AffineMatrix2D | None
        )
        assert isinstance(top_level._behaviors, set)

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
            (enums.Position.NOOP, enums.Position.TOP | enums.Position.LEFT),
            (enums.Position.LEFT, enums.Position.LEFT),
            (enums.Position.RIGHT, enums.Position.RIGHT),
            (
                enums.Position.TOP | enums.Position.RIGHT,
                enums.Position.TOP | enums.Position.RIGHT,
            ),
        ],
    )
    def test_init_anchor_is_set_unittest(
        self, position: enums.Position, expected_anchor: enums.Position
    ) -> None:
        """Anchor is set after init."""
        top_level = component.Component(
            parent=None, width=1, height=1, anchor=position
        )

        assert top_level._anchor is expected_anchor

    def test_anchor_is_set_as_top_left_when_omitted_unittest(self) -> None:
        """Anchor is set as TOP LEFT after init when omitted."""
        top_level = component.Component(parent=None, width=1, height=1)

        assert top_level._anchor is enums.Position.TOP | enums.Position.LEFT


class TestComponentFullScreen:
    """Test Component full_screen."""

    def test_full_screen_component_has_attributes_unittest(self) -> None:
        """Full screen component has proper attributes."""
        top_level = component.Component.full_screen(
            parent=None, anchor=enums.Position.LEFT
        )

        assert top_level.parent is None
        assert len(top_level.children) == 0
        assert top_level._x == 0
        assert top_level._y == 0
        assert top_level._width == constants.Dimensions.WIDTH
        assert top_level._height == constants.Dimensions.HEIGHT
        assert top_level._scale == 1.0
        assert top_level._angle == 0.0
        assert top_level._anchor is enums.Position.LEFT


class TestComponentScreenSpaceProperty:
    """Test Component screen_space property."""

    def test_screen_space_returns_x_y_tuple_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return absolute (x, y) tuple."""
        top_level = component.Component.full_screen(parent=None)

        world_matrix = matrix.AffineMatrix2D()
        mock_get_world = mocker.patch.object(
            top_level, "_get_world_matrix", return_value=world_matrix
        )
        mock_transform = mocker.patch.object(
            world_matrix, "transform_point", return_value=(10, 15)
        )

        abs_x, abs_y = top_level.screen_space

        assert abs_x == 10
        assert abs_y == 15
        mock_get_world.assert_called_once()
        mock_transform.assert_called_once_with(0, 0)


class TestComponentXProperty:
    """Test Component x property."""

    @pytest.mark.parametrize(
        "position, expected_x",
        [
            (enums.Position.TOP | enums.Position.LEFT, 2 + 3),
            (enums.Position.TOP | enums.Position.MIDDLE, 2 + 3 - 3),
            (enums.Position.TOP | enums.Position.RIGHT, 2 + 3 - 6),
            (enums.Position.NOOP | enums.Position.RIGHT, 2 + 3 - 6),
        ],
    )
    def test_x_gets_absolute_x_on_anchor_unittest(
        self, position: enums.Position, expected_x: int
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
        [enums.Position.LEFT, enums.Position.MIDDLE, enums.Position.RIGHT],
    )
    def test_x_sets_absolute_x_unittest(
        self, mocker: pytest_mock.MockerFixture, position: enums.Position
    ) -> None:
        """X sets the absolute x value."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level, x=3, y=4, width=6, height=8, anchor=position
        )

        mock_invalidate = mocker.patch.object(
            component.Component, "_invalidate_transform", return_value=None
        )

        child.x += 100

        # Relative position is expected to not depend on anchor
        assert child._x == 103
        mock_invalidate.assert_called_once()

    def test_x_does_not_call_invalidate_transform_on_same_x_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Do not call _invalidate_transform when x does not change."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        spy_invalidate = mocker.spy(top_level, "_invalidate_transform")

        top_level.x += 0

        spy_invalidate.assert_not_called()


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

    def test_x_rel_sets_relative_x_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """X_rel sets x position relative to parent."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level, x=3, y=4, width=6, height=8
        )
        mock_top_level_invalidate = mocker.patch.object(
            top_level, "_invalidate_transform", return_value=None
        )
        mock_child_invalidate = mocker.patch.object(
            child, "_invalidate_transform", return_value=None
        )

        top_level.x_rel = 5
        child.x_rel = 6

        assert top_level._x == 5
        assert child._x == 6
        mock_top_level_invalidate.assert_called_once()
        mock_child_invalidate.assert_called_once()

    def test_x_rel_does_not_call_invalidate_transform_on_same_x_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Do not call _invalidate_transform when x_rel does not change."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        spy_invalidate = mocker.spy(top_level, "_invalidate_transform")

        top_level.x_rel += 0

        assert top_level._x == 2
        spy_invalidate.assert_not_called()


class TestComponentYProperty:
    """Test Component y property."""

    @pytest.mark.parametrize(
        "position, expected_y",
        [
            (enums.Position.LEFT | enums.Position.TOP, 4 + 5),
            (enums.Position.LEFT | enums.Position.MIDDLE, 4 + 5 - 4),
            (enums.Position.LEFT | enums.Position.BOTTOM, 4 + 5 - 8),
            (enums.Position.NOOP | enums.Position.BOTTOM, 4 + 5 - 8),
        ],
    )
    def test_y_gets_absolute_y_on_anchor_unittest(
        self, position: enums.Position, expected_y: int
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
        [enums.Position.TOP, enums.Position.MIDDLE, enums.Position.BOTTOM],
    )
    def test_y_sets_absolute_y_unittest(
        self, mocker: pytest_mock.MockerFixture, position: enums.Position
    ) -> None:
        """X sets the absolute x value."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level, x=3, y=4, width=6, height=8, anchor=position
        )
        mock_invalidate = mocker.patch.object(
            component.Component, "_invalidate_transform", return_value=None
        )

        child.y += 100

        # Relative position is expected to not depend on anchor
        assert child._y == 104
        mock_invalidate.assert_called_once()

    def test_y_does_not_call_invalidate_transform_on_same_y_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Do not call _invalidate_transform when y does not change."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        spy_invalidate = mocker.spy(top_level, "_invalidate_transform")

        top_level.y += 0

        spy_invalidate.assert_not_called()


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

    def test_y_rel_sets_relative_y_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Y_rel sets y position relative to parent."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        child = component.Component(
            parent=top_level, x=2, y=5, width=6, height=8
        )
        mock_top_level_invalidate = mocker.patch.object(
            top_level, "_invalidate_transform", return_value=None
        )
        mock_child_invalidate = mocker.patch.object(
            child, "_invalidate_transform", return_value=None
        )

        top_level.y_rel = 10
        child.y_rel = 11

        assert top_level._y == 10
        assert child._y == 11
        mock_top_level_invalidate.assert_called_once()
        mock_child_invalidate.assert_called_once()

    def test_y_rel_does_not_call_invalidate_transform_on_same_y_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Do not call _invalidate_transform when y_rel does not change."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )
        spy_invalidate = mocker.spy(top_level, "_invalidate_transform")

        top_level.y_rel += 0

        assert top_level._y == 4
        spy_invalidate.assert_not_called()


class TestComponentScaleProperty:
    """Test Component scale property."""

    def test_scale_gets_scale_unittest(self) -> None:
        """Get scale attribute."""
        top_level = component.Component.full_screen(parent=None)
        top_level._scale = 1.5

        assert top_level.scale == 1.5

    def test_scale_sets_scale_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Set scale attribute and invalidate transform."""
        top_level = component.Component.full_screen(parent=None)
        mock_invalidate = mocker.patch.object(
            top_level, "_invalidate_transform", return_value=None
        )

        top_level.scale = 1.5

        assert top_level._scale == 1.5
        mock_invalidate.assert_called_once()

    def test_scale_does_not_call_invalidate_transform_on_same_scale_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Do not call _invalidate_transform when scale does not change."""
        top_level = component.Component.full_screen(parent=None)
        top_level._scale = 1.5
        mock_invalidate = mocker.patch.object(
            top_level, "_invalidate_transform", return_value=None
        )

        top_level.scale += 0

        assert top_level._scale == 1.5
        mock_invalidate.assert_not_called()


class TestComponentAngleProperty:
    """Test Component angle property."""

    def test_angle_gets_angle_unittest(self) -> None:
        """Get angle attribute."""
        top_level = component.Component.full_screen(parent=None)
        top_level._angle = 90.0

        assert top_level.angle == 90.0

    def test_angle_sets_angle_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Set angle attribute and invalidate transform."""
        top_level = component.Component.full_screen(parent=None)
        mock_invalidate = mocker.patch.object(
            top_level, "_invalidate_transform", return_value=None
        )

        top_level.angle = 90.0

        assert top_level._angle == 90.0
        mock_invalidate.assert_called_once()

    def test_angle_does_not_call_invalidate_transform_on_same_angle_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Do not call _invalidate_transform when angle does not change."""
        top_level = component.Component.full_screen(parent=None)
        top_level._angle = 90.0
        mock_invalidate = mocker.patch.object(
            top_level, "_invalidate_transform", return_value=None
        )

        top_level.angle += 0

        assert top_level._angle == 90.0
        mock_invalidate.assert_not_called()


class TestComponentAnchorProperty:
    """Test Component anchor property."""

    @pytest.mark.parametrize(
        "position, expected_anchor",
        [
            (enums.Position.TOP, enums.Position.TOP),
            (enums.Position.MIDDLE, enums.Position.MIDDLE),
            (
                enums.Position.TOP | enums.Position.MIDDLE,
                enums.Position.TOP | enums.Position.MIDDLE,
            ),
            (enums.Position.NOOP, enums.Position.TOP | enums.Position.LEFT),
        ],
    )
    def test_anchor_gets_component_anchor_unittest(
        self, position: enums.Position, expected_anchor: enums.Position
    ) -> None:
        """Anchor gets the component anchor."""
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8, anchor=position
        )

        assert top_level.anchor is expected_anchor

    @pytest.mark.parametrize(
        "position, expected_anchor",
        [
            (enums.Position.TOP, enums.Position.TOP),
            (enums.Position.MIDDLE, enums.Position.MIDDLE),
            (
                enums.Position.TOP | enums.Position.MIDDLE,
                enums.Position.TOP | enums.Position.MIDDLE,
            ),
            (enums.Position.NOOP, enums.Position.TOP | enums.Position.LEFT),
        ],
    )
    def test_anchor_sets_component_anchor_unittest(
        self, position: enums.Position, expected_anchor: enums.Position
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


class TestComponentAddBehavior:
    """Test Component add_behavior."""

    def test_add_behavior_to_component_unittest(self) -> None:
        """Add behavior to component."""
        top_level = component.Component.full_screen(parent=None)
        behavior = hold.HoldBehavior()

        top_level.add_behavior(behavior)

        assert len(top_level._behaviors) == 1
        assert behavior in top_level._behaviors

    def test_add_replace_behavior_unittest(self) -> None:
        """Replace present behavior with new behavior."""
        top_level = component.Component.full_screen(parent=None)
        behavior1 = hold.HoldBehavior()
        behavior2 = hold.HoldBehavior()
        top_level._behaviors.add(behavior1)

        top_level.add_behavior(behavior2)

        assert len(top_level._behaviors) == 1
        assert behavior2 in top_level._behaviors


class TestComponentGetBehavior:
    """Test Component get_behavior."""

    def test_get_present_behavior_unittest(self) -> None:
        """Get present behavior."""
        top_level = component.Component.full_screen(parent=None)
        behavior1 = hold.HoldBehavior()
        behavior2 = drag.DragBehavior()
        top_level._behaviors.update((behavior1, behavior2))

        result = top_level.get_behavior(drag.DragBehavior)

        assert result is behavior2

    def test_get_no_present_behavior_unittest(self) -> None:
        """Return None when behavior is not present."""
        top_level = component.Component.full_screen(parent=None)
        behavior = hold.HoldBehavior()
        top_level._behaviors.add(behavior)

        result = top_level.get_behavior(drag.DragBehavior)

        assert result is None


class TestComponentRemoveBehavior:
    """Test Component remove_behavior."""

    def test_remove_present_behavior_unittest(self) -> None:
        """Remove present behavior."""
        top_level = component.Component.full_screen(parent=None)
        behavior1 = hold.HoldBehavior()
        behavior2 = drag.DragBehavior()
        top_level._behaviors.update((behavior1, behavior2))

        top_level.remove_behavior(behavior1)

        assert len(top_level._behaviors) == 1
        assert behavior2 in top_level._behaviors

    def test_remove_no_present_behavior_unittest(self) -> None:
        """Remove nothing if behavior is not present."""
        top_level = component.Component.full_screen(parent=None)
        behavior1 = hold.HoldBehavior()
        behavior2 = drag.DragBehavior()
        top_level._behaviors.add(behavior1)

        top_level.remove_behavior(behavior2)

        assert len(top_level._behaviors) == 1
        assert behavior1 in top_level._behaviors


class TestComponentRemoveBehaviors:
    """Test Component remove_behaviors."""

    def test_remove_all_behaviors_unittest(self) -> None:
        """Remove all behaviors."""
        top_level = component.Component.full_screen(parent=None)
        top_level._behaviors.update((hold.HoldBehavior(), drag.DragBehavior()))

        top_level.remove_behaviors()

        assert len(top_level._behaviors) == 0


class TestComponentActivateBehavior:
    """Test Component activate_behavior."""

    def test_activate_present_behavior_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Activate present behavior."""
        top_level = component.Component.full_screen(parent=None)
        behavior = hold.HoldBehavior()
        top_level._behaviors.add(behavior)

        mock_gesture = mocker.Mock()
        mock_handle_gesture = mocker.patch.object(
            behavior, "handle_gesture", return_value=None
        )

        top_level.activate_behavior(behavior, mock_gesture)

        mock_handle_gesture.assert_called_once_with(mock_gesture)

    def test_activate_no_present_behavior_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Activate nothing if behavior is not present."""
        top_level = component.Component.full_screen(parent=None)
        behavior = hold.HoldBehavior()

        mock_handle_gesture = mocker.patch.object(
            behavior, "handle_gesture", return_value=None
        )

        top_level.activate_behavior(behavior, mocker.Mock())

        mock_handle_gesture.assert_not_called()


class TestComponentActivateBehaviors:
    """Test Component activate_behaviors."""

    def test_activate_all_behaviors_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Activate all behaviors."""
        top_level = component.Component.full_screen(parent=None)
        behavior1 = hold.HoldBehavior()
        behavior2 = drag.DragBehavior()
        top_level._behaviors.update((behavior1, behavior2))

        mock_gesture = mocker.Mock()
        mock_handle_gesture1 = mocker.patch.object(
            behavior1, "handle_gesture", return_value=None
        )
        mock_handle_gesture2 = mocker.patch.object(
            behavior2, "handle_gesture", return_value=None
        )

        top_level.activate_behaviors(mock_gesture)

        mock_handle_gesture1.assert_called_once_with(mock_gesture)
        mock_handle_gesture2.assert_called_once_with(mock_gesture)


class TestDispatchGesture:
    """Test dispatch_gesture."""

    def test_dispatch_single_touch_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Dispatch single-touch gesture."""
        top_level = component.Component(
            parent=None, x=5, y=10, width=15, height=20
        )
        gesture = create_gesture()
        gesture.end_point.x = 5
        gesture.end_point.y = 10

        mock_activate = mocker.patch.object(
            top_level, "activate_behaviors", return_value=None
        )

        result = top_level.dispatch_gesture(gesture)

        assert result is top_level
        mock_activate.assert_called_once_with(gesture)

    def test_dispatch_does_not_hit_single_touch_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Dispatch single-touch gesture does not hit component."""
        top_level = component.Component(
            parent=None, x=5, y=10, width=15, height=20
        )
        gesture = create_gesture()
        gesture.end_point.x = 4
        gesture.end_point.y = 10

        mock_activate = mocker.patch.object(
            top_level, "activate_behaviors", return_value=None
        )

        result = top_level.dispatch_gesture(gesture)

        assert result is None
        mock_activate.assert_not_called()

    def test_dispatch_multi_touch_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Dispatch multi-touch gesture."""
        top_level = component.Component(
            parent=None, x=5, y=10, width=15, height=20
        )
        gesture = create_gesture()
        gesture.type = enums.GestureType.MULTI_TOUCH_HOLD
        if gesture.mid_point is not None:
            gesture.mid_point.x = 5
            gesture.mid_point.y = 10

        mock_activate = mocker.patch.object(
            top_level, "activate_behaviors", return_value=None
        )

        result = top_level.dispatch_gesture(gesture)

        assert result is top_level
        mock_activate.assert_called_once_with(gesture)

    def test_dispatch_does_not_hit_multi_touch_gesture_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Dispatch multi-touch gesture does not hit component."""
        top_level = component.Component(
            parent=None, x=5, y=10, width=15, height=20
        )
        gesture = create_gesture()
        gesture.type = enums.GestureType.MULTI_TOUCH_HOLD
        if gesture.mid_point is not None:
            gesture.mid_point.x = 4
            gesture.mid_point.y = 10

        mock_activate = mocker.patch.object(
            top_level, "activate_behaviors", return_value=None
        )

        result = top_level.dispatch_gesture(gesture)

        assert result is None
        mock_activate.assert_not_called()

    def test_dispatch_single_touch_to_child_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Dispatch single-touch gesture to child."""
        top_level = component.Component(
            parent=None, x=5, y=10, width=15, height=20
        )
        child = component.Component(
            parent=top_level, x=5, y=10, width=15, height=20
        )
        gesture = create_gesture()
        gesture.end_point.x = 10
        gesture.end_point.y = 20

        mock_top_level_activate = mocker.patch.object(
            top_level, "activate_behaviors", return_value=None
        )
        mock_child_activate = mocker.patch.object(
            child, "activate_behaviors", return_value=None
        )

        result = top_level.dispatch_gesture(gesture)

        assert result is child
        mock_child_activate.assert_called_once_with(gesture)
        mock_top_level_activate.assert_not_called()

    def test_dispatch_does_not_hit_child_single_touch_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Dispatch single-touch gesture does not hit child."""
        top_level = component.Component(
            parent=None, x=5, y=10, width=15, height=20
        )
        child = component.Component(
            parent=top_level, x=5, y=10, width=15, height=20
        )
        gesture = create_gesture()
        gesture.end_point.x = 9
        gesture.end_point.y = 20

        mock_top_level_activate = mocker.patch.object(
            top_level, "activate_behaviors", return_value=None
        )
        mock_child_activate = mocker.patch.object(
            child, "activate_behaviors", return_value=None
        )

        result = top_level.dispatch_gesture(gesture)

        assert result is top_level
        mock_child_activate.assert_not_called()
        mock_top_level_activate.assert_called_once_with(gesture)


class TestComponentSnapTo:
    """Test Component snap_to."""

    @pytest.mark.parametrize(
        "position, expected_x, expected_y",
        [
            (enums.Position.NOOP, 2, 4),
            (enums.Position.LEFT, 0, 4),
            (enums.Position.MIDDLE, 500, 2000),
            (enums.Position.RIGHT, 1000, 4),
            (enums.Position.TOP, 2, 0),
            (enums.Position.BOTTOM, 2, 4000),
            (enums.Position.BOTTOM | enums.Position.NOOP, 2, 4000),
        ],
    )
    def test_snap_one_position_top_level_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        position: enums.Position,
        expected_x: int,
        expected_y: int,
    ) -> None:
        """Snap has one position for top level component."""
        mocker.patch.object(constants.Dimensions, "WIDTH", 1000)
        mocker.patch.object(constants.Dimensions, "HEIGHT", 4000)
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )

        top_level.snap_to(position)

        assert top_level._x == expected_x
        assert top_level._y == expected_y

    @pytest.mark.parametrize(
        "position1, position2, expected_x, expected_y",
        [
            (enums.Position.TOP, enums.Position.LEFT, 0, 0),
            (enums.Position.TOP, enums.Position.MIDDLE, 50, 0),
            (enums.Position.TOP, enums.Position.RIGHT, 100, 0),
            (enums.Position.MIDDLE, enums.Position.RIGHT, 100, 5),
            (enums.Position.BOTTOM, enums.Position.RIGHT, 100, 10),
            (enums.Position.MIDDLE, enums.Position.BOTTOM, 50, 10),
            (enums.Position.LEFT, enums.Position.BOTTOM, 0, 10),
            (enums.Position.MIDDLE, enums.Position.LEFT, 0, 5),
            (
                enums.Position.NOOP | enums.Position.MIDDLE,
                enums.Position.LEFT,
                0,
                5,
            ),
        ],
    )
    def test_snap_two_positions_top_level_unittest(
        self,
        mocker: pytest_mock.MockerFixture,
        position1: enums.Position,
        position2: enums.Position,
        expected_x: int,
        expected_y: int,
    ) -> None:
        """Snap has two positions for top level component."""
        mocker.patch.object(constants.Dimensions, "WIDTH", 100)
        mocker.patch.object(constants.Dimensions, "HEIGHT", 10)
        top_level = component.Component(
            parent=None, x=2, y=4, width=6, height=8
        )

        top_level.snap_to(position1 | position2)

        assert top_level._x == expected_x
        assert top_level._y == expected_y

    @pytest.mark.parametrize(
        "position, expected_x, expected_y",
        [
            (enums.Position.NOOP, 2, 4),
            (enums.Position.LEFT, 0, 4),
            (enums.Position.MIDDLE, 500, 2000),
            (enums.Position.RIGHT, 1000, 4),
            (enums.Position.TOP, 2, 0),
            (enums.Position.BOTTOM, 2, 4000),
            (enums.Position.BOTTOM | enums.Position.NOOP, 2, 4000),
        ],
    )
    def test_snap_one_position_child_unittest(
        self, position: enums.Position, expected_x: int, expected_y: int
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
            (enums.Position.TOP, enums.Position.LEFT, 0, 0),
            (enums.Position.TOP, enums.Position.MIDDLE, 50, 0),
            (enums.Position.TOP, enums.Position.RIGHT, 100, 0),
            (enums.Position.MIDDLE, enums.Position.RIGHT, 100, 5),
            (enums.Position.BOTTOM, enums.Position.RIGHT, 100, 10),
            (enums.Position.MIDDLE, enums.Position.BOTTOM, 50, 10),
            (enums.Position.LEFT, enums.Position.BOTTOM, 0, 10),
            (enums.Position.MIDDLE, enums.Position.LEFT, 0, 5),
            (
                enums.Position.MIDDLE | enums.Position.NOOP,
                enums.Position.LEFT,
                0,
                5,
            ),
        ],
    )
    def test_snap_two_positions_child_unittest(
        self,
        position1: enums.Position,
        position2: enums.Position,
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


class TestComponentWasTouched:
    """Test Component was_touched."""

    def test_touch_returns_true_when_touched_unittest(self) -> None:
        """Return True when the component was touched."""
        top_level = component.Component(
            parent=None, x=5, y=10, width=100, height=200
        )

        assert top_level.was_touched(5, 10)

    def test_touch_returns_false_when_not_touched_unittest(self) -> None:
        """Return False when the component was not touched."""
        top_level = component.Component(
            parent=None, x=5, y=10, width=100, height=200
        )

        assert not top_level.was_touched(4, 10)


class TestComponentInvalidateTransform:
    """Test Component _invalidate_transform."""

    def test_invalidate_does_nothing_on_dirty_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Do not invalidate transform on dirty matrix."""
        top_level = component.Component.full_screen(parent=None)
        child = component.Component.full_screen(parent=top_level)
        spy_invalidate_child1 = mocker.spy(child, "_invalidate_transform")

        top_level._invalidate_transform()

        spy_invalidate_child1.assert_not_called()
        assert top_level._matrix_dirty
        assert child._matrix_dirty

    def test_invalidate_propagates_to_children_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Invalidate transform for all children with False dirty matrix."""
        top_level = component.Component.full_screen(parent=None)
        top_level._matrix_dirty = False

        child1 = component.Component.full_screen(parent=top_level)
        child1._matrix_dirty = False
        spy_invalidate_child1 = mocker.spy(child1, "_invalidate_transform")

        grandchild = component.Component.full_screen(parent=top_level)
        grandchild._matrix_dirty = False
        spy_invalidate_grandchild = mocker.spy(
            grandchild, "_invalidate_transform"
        )

        child2 = component.Component.full_screen(parent=top_level)
        child2._matrix_dirty = False
        spy_invalidate_child2 = mocker.spy(child2, "_invalidate_transform")

        top_level._invalidate_transform()

        spy_invalidate_child1.assert_called_once()
        spy_invalidate_grandchild.assert_called_once()
        spy_invalidate_child2.assert_called_once()
        assert top_level._matrix_dirty
        assert child1._matrix_dirty
        assert grandchild._matrix_dirty
        assert child2._matrix_dirty


class TestComponentGetAnchorOffsets:
    """Test Component _get_anchor_offsets."""

    @pytest.mark.parametrize(
        "position, expected_x, expected_y",
        [
            (enums.Position.LEFT, 0, 0),
            (enums.Position.MIDDLE, 500, 2000),
            (enums.Position.RIGHT, 1000, 0),
            (enums.Position.TOP, 0, 0),
            (enums.Position.BOTTOM, 0, 4000),
            (enums.Position.BOTTOM | enums.Position.NOOP, 0, 4000),
        ],
    )
    def test_get_correct_anchor_offsets_on_one_position_unittest(
        self, position: enums.Position, expected_x: int, expected_y: int
    ) -> None:
        """Get correct anchor offsets on anchor with one position."""
        top_level = component.Component(
            parent=None, width=1000, height=4000, anchor=position
        )

        off_x, off_y = top_level._get_anchor_offsets()

        assert off_x == expected_x
        assert off_y == expected_y

    @pytest.mark.parametrize(
        "position1, position2, expected_x, expected_y",
        [
            (enums.Position.TOP, enums.Position.LEFT, 0, 0),
            (enums.Position.TOP, enums.Position.MIDDLE, 50, 0),
            (enums.Position.TOP, enums.Position.RIGHT, 100, 0),
            (enums.Position.MIDDLE, enums.Position.RIGHT, 100, 5),
            (enums.Position.BOTTOM, enums.Position.RIGHT, 100, 10),
            (enums.Position.MIDDLE, enums.Position.BOTTOM, 50, 10),
            (enums.Position.LEFT, enums.Position.BOTTOM, 0, 10),
            (enums.Position.MIDDLE, enums.Position.LEFT, 0, 5),
            (
                enums.Position.MIDDLE | enums.Position.NOOP,
                enums.Position.LEFT,
                0,
                5,
            ),
        ],
    )
    def test_get_correct_anchor_offsets_on_two_positions_unittest(
        self,
        position1: enums.Position,
        position2: enums.Position,
        expected_x: int,
        expected_y: int,
    ) -> None:
        """Get correct anchor offsets on anchor with two positions."""
        top_level = component.Component(
            parent=None, width=100, height=10, anchor=position1 | position2
        )

        off_x, off_y = top_level._get_anchor_offsets()

        assert off_x == expected_x
        assert off_y == expected_y


class TestComponentGetLocalMatrix:
    """Test Component _get_local_matrix."""

    def test_get_returns_cached_matrix_unittest(self) -> None:
        """Return cached local matrix."""
        mat = matrix.AffineMatrix2D()
        top_level = component.Component.full_screen(parent=None)
        top_level._matrix_dirty = False
        top_level._local_matrix = mat

        local_matrix = top_level._get_local_matrix()

        assert local_matrix is mat

    def test_get_returns_translate_x_matrix_unittest(self) -> None:
        """Return local matrix with x translation."""
        top_level = component.Component(parent=None, width=10, height=15)
        top_level._x = 5

        local_matrix = top_level._get_local_matrix()
        a, b, c, d, tx, ty = local_matrix._data

        assert a == 1.0
        assert b == 0.0
        assert c == 0.0
        assert d == 1.0
        assert tx == 5.0
        assert ty == 0.0

    def test_get_returns_translate_y_matrix_unittest(self) -> None:
        """Return local matrix with y translation."""
        top_level = component.Component(parent=None, width=10, height=15)
        top_level._y = 5

        local_matrix = top_level._get_local_matrix()
        a, b, c, d, tx, ty = local_matrix._data

        assert a == 1.0
        assert b == 0.0
        assert c == 0.0
        assert d == 1.0
        assert tx == 0.0
        assert ty == 5.0

    def test_get_returns_rotate_matrix_unittest(self) -> None:
        """Return local matrix with rotate."""
        top_level = component.Component(parent=None, width=10, height=15)
        top_level._angle = 90.0  # degrees

        local_matrix = top_level._get_local_matrix()
        a, b, c, d, tx, ty = local_matrix._data

        assert math.isclose(a, 0.0, abs_tol=1e-15)
        assert b == 1.0
        assert c == -1.0
        assert math.isclose(d, 0.0, abs_tol=1e-15)
        assert tx == 0.0
        assert ty == 0.0

    def test_get_returns_scale_matrix_unittest(self) -> None:
        """Return local matrix with scale."""
        top_level = component.Component(parent=None, width=10, height=15)
        top_level._scale = 2.0

        local_matrix = top_level._get_local_matrix()
        a, b, c, d, tx, ty = local_matrix._data

        assert a == 2.0
        assert b == 0.0
        assert c == 0.0
        assert d == 2.0
        assert tx == 0.0
        assert ty == 0.0

    @pytest.mark.parametrize(
        "position, expected_tx, expected_ty",
        [
            (enums.Position.LEFT, 0, 0),
            (enums.Position.MIDDLE, -5, -20),
            (enums.Position.RIGHT, -10, 0),
            (enums.Position.TOP, 0, 0),
            (enums.Position.BOTTOM, 0, -40),
            (enums.Position.BOTTOM | enums.Position.NOOP, 0, -40),
        ],
    )
    def test_get_returns_anchor_translate_matrix_unittest(
        self,
        position: enums.Position,
        expected_tx: float,
        expected_ty: float,
    ) -> None:
        """Return local matrix with anchor translation."""
        top_level = component.Component(parent=None, width=10, height=40)
        top_level._anchor = position

        local_matrix = top_level._get_local_matrix()
        a, b, c, d, tx, ty = local_matrix._data

        assert a == 1.0
        assert b == 0.0
        assert c == 0.0
        assert d == 1.0
        assert tx == expected_tx
        assert ty == expected_ty


class TestComponentGetWorldMatrix:
    """Test Component _get_world_matrix."""

    def test_get_returns_cached_matrix_unittest(self) -> None:
        """Return cached world matrix."""
        mat = matrix.AffineMatrix2D()
        top_level = component.Component.full_screen(parent=None)
        top_level._matrix_dirty = False
        top_level._world_matrix = mat

        world_matrix = top_level._get_world_matrix()

        assert world_matrix is mat

    def test_get_returns_local_matrix_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return local matrix when parent is None."""
        local_mat = matrix.AffineMatrix2D()
        top_level = component.Component.full_screen(parent=None)
        mocker.patch.object(
            top_level, "_get_local_matrix", return_value=local_mat
        )

        world_matrix = top_level._get_world_matrix()

        assert world_matrix is local_mat

    def test_get_returns_world_matrix_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Return multiplied matrix up the tree."""
        top_level = component.Component.full_screen(parent=None)
        child = component.Component.full_screen(parent=top_level)

        top_level_local = matrix.AffineMatrix2D()
        child_local = matrix.AffineMatrix2D()
        mock_top_level_get_local = mocker.patch.object(
            top_level, "_get_local_matrix", return_value=top_level_local
        )
        mocker.patch.object(
            child, "_get_local_matrix", return_value=child_local
        )
        mock_multiply = mocker.patch.object(
            matrix.AffineMatrix2D, "multiply", return_value=None
        )
        spy_top_level_get_world = mocker.spy(top_level, "_get_world_matrix")
        spy_child_get_world = mocker.spy(child, "_get_world_matrix")

        child._get_world_matrix()

        spy_child_get_world.assert_called_once()
        spy_top_level_get_world.assert_called_once()
        mock_multiply.assert_called_once()
        mock_top_level_get_local.return_value.multiply.assert_called_once_with(
            child_local
        )
        assert not top_level._matrix_dirty
        assert not child._matrix_dirty


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
