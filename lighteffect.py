from typing import Tuple
from effect import Effect
from calc import Calc
from curve import Curve
import numpy as np

Color_ = Tuple[int, int, int]
Coords_ = Tuple[float, float]


class LightEffect(Effect):
    intensity: float
    coords: Coords_
    color: Color_
    intensity_curve: Curve

    def __init__(
        self,
        coords: Coords_ = (0, 0),
        color: Color_ = (255, 255, 255),
        intensity: float = 1,
    ) -> None:
        self.coords = (
            coords
            if type(coords) != str
            else tuple([float(c) for c in coords.split(",")])
        )
        self.color = color
        self.intensity = intensity

    def set_color(self, color: Color_):
        self.color = color

    def set_intensity(self, intensity: float):
        self.intensity = intensity

    def set_coords(self, coords: Coords_):
        self.coords = Coords_

    def apply(self, other: Calc):
        if self.intensity < 0.001:
            return
        vx, vy = other.coords
        vx -= self.coords[0]
        vy -= self.coords[1]

        intensity_matrix = np.meshgrid(
            vx + np.arange(other.width), vy + np.arange(other.height)
        )
        intensity_matrix = np.sqrt(intensity_matrix[0] ** 2 + intensity_matrix[1] ** 2)

        intensity_matrix = self.intensity_curve.calc(intensity_matrix / self.intensity)
