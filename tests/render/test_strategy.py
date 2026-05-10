import collections

import pytest
import pytest_mock

from pireaderos.common import enums
from pireaderos.render import strategy


@pytest.fixture
def mock_rectangle(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock the rectangle function."""
    return mocker.patch("pireaderos.render.strategy.step.rectangle")


@pytest.fixture
def mock_rounded_rectangle(
    mocker: pytest_mock.MockerFixture,
) -> pytest_mock.MockType:
    """Mock the rounded_rectangle function."""
    return mocker.patch("pireaderos.render.strategy.step.rounded_rectangle")


@pytest.fixture
def mock_percent(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock the models.Percent class."""
    return mocker.patch("pireaderos.render.strategy.models.Percent")


class TestRenderStrategyInitialization:
    """Test RenderStrategy initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        a_strategy = strategy.RenderStrategy()

        assert isinstance(a_strategy.steps, collections.deque)
        assert a_strategy.render_dirty


class TestRenderStrategyDrawRectangle:
    """Test RenderStrategy draw_rectangle."""

    def test_draw_rectangle_assigns_step_unittest(
        self, mock_rectangle: pytest_mock.MockType
    ) -> None:
        """Assign a draw rectangle step."""
        a_strategy = strategy.RenderStrategy()
        a_strategy.render_dirty = False

        a_strategy.draw_rectangle(
            x=5,
            y=10,
            width=15,
            height=20,
            fill=enums.Color.WHITE,
            thickness=25,
            outline=enums.Color.BLACK,
        )

        mock_rectangle.assert_called_once_with(
            5, 10, 15, 20, enums.Color.WHITE, 25, enums.Color.BLACK
        )
        assert len(a_strategy.steps) == 1
        assert mock_rectangle.return_value in a_strategy.steps
        assert a_strategy.render_dirty


class TestRenderStrategyDrawRoundedRectangle:
    """Test RenderStrategy draw_rounded_rectangle."""

    def test_draw_rounded_rectangle_assigns_step_unittest(
        self, mock_rounded_rectangle: pytest_mock.MockType
    ) -> None:
        """Assign a draw rounded rectangle step."""
        a_strategy = strategy.RenderStrategy()
        a_strategy.render_dirty = False
        corners = (True, False, False, False)

        a_strategy.draw_rounded_rectangle(
            x=5,
            y=10,
            width=15,
            height=20,
            fill=enums.Color.WHITE,
            thickness=25,
            outline=enums.Color.BLACK,
            radius=30,
            corners=corners,
        )

        mock_rounded_rectangle.assert_called_once_with(
            5,
            10,
            15,
            20,
            enums.Color.WHITE,
            25,
            enums.Color.BLACK,
            30,
            corners,
        )
        assert len(a_strategy.steps) == 1
        assert mock_rounded_rectangle.return_value in a_strategy.steps
        assert a_strategy.render_dirty


class TestRenderStrategyFillBackground:
    """Test RenderStrategy fill_background."""

    def test_fill_background_assigns_step_unittest(
        self,
        mock_rectangle: pytest_mock.MockType,
        mock_percent: pytest_mock.MockType,
    ) -> None:
        """Assign a fill background step."""
        a_strategy = strategy.RenderStrategy()
        a_strategy.render_dirty = False

        a_strategy.fill_background(enums.Color.WHITE)

        mock_percent.assert_called_with(100)
        mock_rectangle.assert_called_once_with(
            0,
            0,
            mock_percent.return_value,
            mock_percent.return_value,
            enums.Color.WHITE,
            1,
            None,
        )
        assert len(a_strategy.steps) == 1
        assert mock_rectangle.return_value in a_strategy.steps
        assert a_strategy.render_dirty
