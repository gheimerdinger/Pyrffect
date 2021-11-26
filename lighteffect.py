from typing import Tuple
from effect import Effect
from calc import Calc
from curve import CappedCurve, CappedInCurve, Curve, PolynomCurve
import numpy as np

from pyrffect_global import rgb_to_tsv, tsv_to_rgb

Color_ = Tuple[int, int, int]
Coords_ = Tuple[float, float]


class LightEffect(Effect):
    intensity: float
    coords: Coords_
    color: Color_
    intensity_curve: Curve
    dist_step: float
    color_tsv: Tuple[float, float, float]

    def __init__(
        self,
        coords: Coords_ = (0, 0),
        color: Color_ = (255, 255, 255),
        intensity: float = 1,
        dist_step: float = 100,
    ) -> None:
        self.coords = (
            coords
            if type(coords) != str
            else tuple([float(c) for c in coords.split(",")])
        )
        self.color = [color[0], color[1], color[2], 255]
        self.intensity = float(intensity)
        self.dist_step = float(dist_step)
        self.color_tsv = rgb_to_tsv(np.array([[self.color + [255]]]))[:-1]
        self.color_tsv = tuple([e[0, 0] for e in self.color_tsv])
        self.intensity_curve = PolynomCurve(
            [
                -18.694631936361304,
                103.51374748872877,
                -239.58171720999894,
                305.18504534599487,
                -233.87970238288946,
                106.14527986104831,
                -23.16527350950359,
                -0.5214952700248797,
                0.9990813317288378,
            ]
        )
        self.intensity_curve = CappedInCurve(self.intensity_curve, maxi=1)

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
            vx + np.arange(other.height), vy + np.arange(other.width)
        )
        intensity_matrix = np.sqrt(intensity_matrix[0] ** 2 + intensity_matrix[1] ** 2)

        intensity_matrix = self.intensity_curve.calc(
            intensity_matrix / self.dist_step / self.intensity ** 2
        )

        t, s, v, alpha = rgb_to_tsv(other.out_buffer)
        tr, sr, vr = self.color_tsv
        delta_t = tr - t
        t += (
            (np.cos(2 * np.math.pi / 360 * delta_t) + 1.0)
            / 2.0
            * intensity_matrix
            * delta_t
        )
        s += sr * intensity_matrix ** 2
        s[s > 1] = 1
        v += vr * intensity_matrix ** 2
        v[v > 1] = 1
        other.out_buffer = tsv_to_rgb(t, s, v, alpha)
