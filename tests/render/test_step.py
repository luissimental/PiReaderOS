import pytest_mock

from pireaderos.common import enums, models
from pireaderos.render import pillow, step


class TestRenderStepInitialization:
    """Test RenderStep initialization."""

    def test_init_is_working_unittest(self) -> None:
        """All attributes are present."""
        method = pillow.ImageDrawMethod.RECTANGLE
        a_step = step.RenderStep(method)

        assert a_step.method is method
        assert isinstance(a_step.kwargs, dict)

    def test_init_kwargs_are_stored_unittest(self) -> None:
        """Kwargs are stored in object."""
        a_step = step.RenderStep(
            pillow.ImageDrawMethod.RECTANGLE, arg1=1, arg2=2, arg3=3
        )

        assert len(a_step.kwargs) == 3
        assert a_step.kwargs["arg1"] == 1
        assert a_step.kwargs["arg2"] == 2
        assert a_step.kwargs["arg3"] == 3


class TestRenderStepResolveKwargs:
    """Test RenderStep resolve_kwargs."""

    def test_resolve_returns_original_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Method does not need resolved kwargs."""
        a_step = step.RenderStep(mocker.Mock())

        # Does not raise error
        a_step.resolve_kwargs(mocker.Mock())


class TestRectangle:
    """Test rectangle."""

    def test_rectangle_step_has_attributes_unittest(self) -> None:
        """Rectangle step has attributes."""
        rect_step = step.rectangle(
            x=5,
            y=10,
            width=15,
            height=20,
            fill=enums.Color.WHITE,
            thickness=25,
            outline=enums.Color.BLACK,
        )

        assert len(rect_step.kwargs) == 7
        assert rect_step.kwargs["x"] == 5
        assert rect_step.kwargs["y"] == 10
        assert rect_step.kwargs["width"] == 15
        assert rect_step.kwargs["height"] == 20
        assert rect_step.kwargs["fill"] is enums.Color.WHITE
        assert rect_step.kwargs["thickness"] == 25
        assert rect_step.kwargs["outline"] is enums.Color.BLACK

    def test_rectangle_resolve_x_and_y_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Resolve rectangle x and y."""
        rect_step = step.rectangle(
            x=5,
            y=10,
            width=200,
            height=10,
            fill=enums.Color.WHITE,
            thickness=25,
            outline=enums.Color.BLACK,
        )
        mock_component = mocker.Mock()
        mock_component.screen_space = 2000, 1000
        mock_component.scale = 2.0

        resolved = rect_step.resolve_kwargs(mock_component)

        assert len(resolved) == 7
        assert resolved["x"] == 2005
        assert resolved["y"] == 1010

    def test_rectangle_resolve_width_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Resolve rectangle width kwarg."""
        rect_step = step.rectangle(
            x=5,
            y=10,
            width=models.Percent(50),
            height=10,
            fill=enums.Color.WHITE,
            thickness=25,
            outline=enums.Color.BLACK,
        )
        mock_component = mocker.Mock()
        mock_component.screen_space = 2000, 1000
        mock_component.width = 200
        mock_component.scale = 2.0

        resolved = rect_step.resolve_kwargs(mock_component)

        assert len(resolved) == 7
        assert resolved["width"] == 100
        assert resolved["height"] == 20

    def test_rectangle_resolve_height_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Resolve rectangle height kwarg."""
        rect_step = step.rectangle(
            x=5,
            y=10,
            width=200,
            height=models.Percent(50),
            fill=enums.Color.WHITE,
            thickness=25,
            outline=enums.Color.BLACK,
        )
        mock_component = mocker.Mock()
        mock_component.screen_space = 2000, 1000
        mock_component.height = 10
        mock_component.scale = 2.0

        resolved = rect_step.resolve_kwargs(mock_component)

        assert len(resolved) == 7
        assert resolved["width"] == 400
        assert resolved["height"] == 5


class TestRoundedRectangle:
    """Test rounded_rectangle."""

    def test_rounded_rectangle_step_has_attributes_unittest(self) -> None:
        """Rounded rectangle step has attributes."""
        corners = (True, False, False, False)
        rect_step = step.rounded_rectangle(
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

        assert len(rect_step.kwargs) == 9
        assert rect_step.kwargs["x"] == 5
        assert rect_step.kwargs["y"] == 10
        assert rect_step.kwargs["width"] == 15
        assert rect_step.kwargs["height"] == 20
        assert rect_step.kwargs["fill"] is enums.Color.WHITE
        assert rect_step.kwargs["thickness"] == 25
        assert rect_step.kwargs["outline"] is enums.Color.BLACK
        assert rect_step.kwargs["radius"] == 30
        assert rect_step.kwargs["corners"] is corners

    def test_rounded_rectangle_resolve_x_and_y_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Resolve rounded rectangle x and y."""
        rect_step = step.rounded_rectangle(
            x=5,
            y=10,
            width=15,
            height=20,
            fill=enums.Color.WHITE,
            thickness=25,
            outline=enums.Color.BLACK,
            radius=30,
            corners=None,
        )
        mock_component = mocker.Mock()
        mock_component.screen_space = 2000, 1000
        mock_component.scale = 2.0

        resolved = rect_step.resolve_kwargs(mock_component)

        assert len(resolved) == 9
        assert resolved["x"] == 2005
        assert resolved["y"] == 1010

    def test_rounded_rectangle_resolve_width_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Resolve rounded rectangle width kwarg."""
        rect_step = step.rounded_rectangle(
            x=5,
            y=10,
            width=models.Percent(50),
            height=10,
            fill=enums.Color.WHITE,
            thickness=25,
            outline=enums.Color.BLACK,
            radius=30,
            corners=None,
        )
        mock_component = mocker.Mock()
        mock_component.screen_space = 2000, 1000
        mock_component.width = 200
        mock_component.scale = 2.0

        resolved = rect_step.resolve_kwargs(mock_component)

        assert len(resolved) == 9
        assert resolved["width"] == 100
        assert resolved["height"] == 20

    def test_rounded_rectangle_resolve_height_unittest(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Resolve rounded rectangle height kwarg."""
        rect_step = step.rounded_rectangle(
            x=5,
            y=10,
            width=200,
            height=models.Percent(50),
            fill=enums.Color.WHITE,
            thickness=25,
            outline=enums.Color.BLACK,
            radius=30,
            corners=None,
        )
        mock_component = mocker.Mock()
        mock_component.screen_space = 2000, 1000
        mock_component.height = 10
        mock_component.scale = 2.0

        resolved = rect_step.resolve_kwargs(mock_component)

        assert len(resolved) == 9
        assert resolved["width"] == 400
        assert resolved["height"] == 5
