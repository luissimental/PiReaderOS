# pragma: exclude file
import enum


class ImageDrawMethod(enum.Enum):
    """The Pillow ImageDraw methods."""

    RECTANGLE = enum.auto()
    ROUNDED_RECTANGLE = enum.auto()
