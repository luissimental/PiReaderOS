from __future__ import annotations


class AffineMatrix2D:
    """Generate a 2D affine transformation matrix."""

    def __init__(
        self,
        a: float = 1.0,
        b: float = 0.0,
        c: float = 0.0,
        d: float = 1.0,
        tx: float = 0.0,
        ty: float = 0.0,
    ) -> None:
        """Initialize a 2D affine transformation matrix.

        The affine matrix is of the form::

          [ a, c, tx ]
          [ b, d, ty ]
          [ 0, 0, 1  ]

        """
        self._data = (a, b, c, d, tx, ty)

    def multiply(self, other: AffineMatrix2D) -> AffineMatrix2D:
        """Multiply by another affine matrix."""
        a1, b1, c1, d1, tx1, ty1 = self._data
        a2, b2, c2, d2, tx2, ty2 = other._data

        return AffineMatrix2D(
            (a1 * a2) + (c1 * b2),
            (b1 * a2) + (d1 * b2),
            (a1 * c2) + (c1 * d2),
            (b1 * c2) + (d1 * d2),
            (a1 * tx2) + (c1 * ty2) + tx1,
            (b1 * tx2) + (d1 * ty2) + ty1,
        )

    def transform_point(self, x: float, y: float) -> tuple[float, float]:
        """Transform a point according to the affine matrix."""
        a, b, c, d, tx, ty = self._data
        return (
            (a * x) + (c * y) + tx,
            (b * x) + (d * y) + ty,
        )

    def inverse(self) -> AffineMatrix2D:
        """Compute the inverse of the affine matrix."""
        a, b, c, d, tx, ty = self._data

        det = a * d - b * c
        if det == 0:
            return AffineMatrix2D()

        inv_det = 1.0 / det

        return AffineMatrix2D(
            d * inv_det,
            -b * inv_det,
            -c * inv_det,
            a * inv_det,
            (c * ty - d * tx) * inv_det,
            (b * tx - a * ty) * inv_det,
        )
