import collections

from pireaderos.common import enums, models
from pireaderos.render import step


class RenderStrategy:
    """The container for a component's rendering steps.

    Steps are stored in a deque to maintain rendering order. Steps at the end
    of the deque are rendered last, appearing on top of earlier steps.

    Attributes:
      steps:
        The deque of rendering steps, ordered from bottom to top visually.
      render_dirty:
        A flag for detecting changes in rendering steps.

    """

    def __init__(self) -> None:
        self.steps = collections.deque[step.RenderStep]()

        # Flag for detecting changes in render
        self.render_dirty: bool = True

    def draw_rectangle(
        self,
        *,
        x: int,
        y: int,
        width: int | models.Percent,
        height: int | models.Percent,
        fill: enums.Color,
        thickness: int = 1,
        outline: enums.Color | None = None,
    ) -> None:
        """Draw a rectangle.

        Args:
          x:
            The x position of the rectangle relative to the component.
          y:
            The y position of the rectangle relative to the component.
          width:
            The width of the rectangle in pixels. May be a percentage of the
            component's width.
          height:
            The height of the rectangle in pixels. May be a percentage of the
            component's height.
          fill:
            The color to fill the rectangle.
          thickness:
            The width of the rectangle's outline.
          outline:
            The color of the rectangles's outline.

        """
        rect_step = step.rectangle(
            x, y, width, height, fill, thickness, outline
        )

        self.steps.append(rect_step)
        self.render_dirty = True

    def draw_rounded_rectangle(
        self,
        *,
        x: int,
        y: int,
        width: int | models.Percent,
        height: int | models.Percent,
        fill: enums.Color,
        thickness: int = 1,
        outline: enums.Color | None = None,
        radius: int,
        corners: tuple[bool, bool, bool, bool] | None = None,
    ) -> None:
        """Draw a rounded rectangle.

        Args:
          x:
            The x position of the rectangle relative to the component.
          y:
            The y position of the rectangle relative to the component.
          width:
            The width of the rectangle in pixels. May be a percentage of the
            component's width.
          height:
            The height of the rectangle in pixels. May be a percentage of the
            component's height.
          fill:
            The color to fill the rectangle.
          thickness:
            The width of the rectangle's outline.
          outline:
            The color of the rectangles's outline.
          radius:
            The radius of the rounded corners in pixels.
          corners:
            A tuple of bools (top left, top right, bottom right, bottom left)
            representing which corners should be rounded. None rounds all of
            the corners.

        """
        rect_step = step.rounded_rectangle(
            x, y, width, height, fill, thickness, outline, radius, corners
        )

        self.steps.append(rect_step)
        self.render_dirty = True

    def fill_background(self, fill: enums.Color, /) -> None:
        """Fill the background.

        Args:
          fill:
            The color to fill the background.

        """
        rect_step = step.rectangle(
            0, 0, models.Percent(100), models.Percent(100), fill, 1, None
        )

        self.steps.appendleft(rect_step)
        self.render_dirty = True
