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
        dist_step: float = 20,
    ) -> None:
        self.coords = (
            coords
            if type(coords) != str
            else tuple([float(c) for c in coords.split(",")])
        )
        if type(color) == str:
            color = [float(e) for e in color.split(",")]
        self.color = tuple([color[0], color[1], color[2], 255])
        self.intensity = float(intensity)
        self.dist_step = float(dist_step)
        N = np.array([[self.color]])
        self.color_tsv = rgb_to_tsv(N)[:-1]
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
        N = np.array([[self.color]])
        self.color_tsv = rgb_to_tsv(N)[:-1]
        self.color_tsv = tuple([e[0, 0] for e in self.color_tsv])

    def set_intensity(self, intensity: float):
        self.intensity = intensity

    def set_coords(self, coords: Coords_):
        self.coords = coords

    def set_dist(self, dist: float):
        self.dist_step = dist

    def apply(self, other: Calc):
        if self.intensity < 0.00001:
            return
        vx, vy = other.coords
        vx -= self.coords[0]
        vy -= self.coords[1]

        intensity_matrix = np.meshgrid(
            vx + np.arange(other.width), vy + np.arange(other.height)
        )  # why is it reversed...
        intensity_matrix = intensity_matrix[0] ** 2 + intensity_matrix[1] ** 2

        intensity_matrix = self.intensity_curve.calc(
            intensity_matrix / self.dist_step ** 2 / self.intensity ** 5
        )

        t, s, v, alpha = rgb_to_tsv(other.out_buffer)
        tr, sr, vr = self.color_tsv
        mask = v < 0.001
        t[mask] = ((tr + 60 * t) % 360)[mask]
        delta_t = tr - t
        t += (
            ((np.cos(2 * np.math.pi / 360 * delta_t) + 1.0) / 2.0) ** 2
            * intensity_matrix
            * delta_t
        )
        self.intensity -= 0.003

        s += sr * intensity_matrix ** 3
        s[s > 1] = 1
        v += vr * intensity_matrix ** 2
        v[v > 1] = 1
        other.out_buffer = tsv_to_rgb(t, s, v, alpha)
