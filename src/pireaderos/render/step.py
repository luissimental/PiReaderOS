from typing import Any

from pireaderos.common import enums, models
from pireaderos.render import pillow
from pireaderos.ui import component


class RenderStep:
    """A step in the rendering process.

    Attributes:
      method:
        The Pillow ImageDraw method used for rendering.
      kwargs:
        The keyword arguments to pass to the Pillow ImageDraw method.

    """

    def __init__(self, method: pillow.ImageDrawMethod, **kwargs: Any) -> None:
        self.method = method
        self.kwargs = kwargs

    def resolve_kwargs(self, owner: component.Component) -> dict[str, Any]:
        """Resolve keyword arguments with component attributes."""
        resolved = self.kwargs.copy()

        if self.method in (
            pillow.ImageDrawMethod.RECTANGLE,
            pillow.ImageDrawMethod.ROUNDED_RECTANGLE,
        ):
            width: int | models.Percent = resolved["width"]
            height: int | models.Percent = resolved["height"]

            if isinstance(width, models.Percent):
                resolved["width"] = int(owner.width * width.amount)
            if isinstance(height, models.Percent):
                resolved["height"] = int(owner.height * height.amount)

        return resolved


def rectangle(
    x: int,
    y: int,
    width: int | models.Percent,
    height: int | models.Percent,
    fill: enums.Color,
    thickness: int,
    outline: enums.Color | None,
) -> RenderStep:
    """Create a draw rectangle step."""
    return RenderStep(
        pillow.ImageDrawMethod.RECTANGLE,
        x=x,
        y=y,
        width=width,
        height=height,
        fill=fill,
        thickness=thickness,
        outline=outline,
    )


def rounded_rectangle(
    x: int,
    y: int,
    width: int | models.Percent,
    height: int | models.Percent,
    fill: enums.Color,
    thickness: int,
    outline: enums.Color | None,
    radius: int,
    corners: tuple[bool, bool, bool, bool] | None,
) -> RenderStep:
    """Create a draw rounded rectangle step."""
    step = rectangle(x, y, width, height, fill, thickness, outline)
    step.method = pillow.ImageDrawMethod.ROUNDED_RECTANGLE
    step.kwargs["radius"] = radius
    step.kwargs["corners"] = corners

    return step
