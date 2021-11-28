from typing import List, Tuple, Union

from numpy.core.fromnumeric import shape
from calc import Calc
from curve import (
    ComposedCurve,
    Curve,
    LinearCurve,
    CappedCurve,
    MulCurve,
    PolynomCurve,
    QuadraticCurve,
    SinCurve,
)
import numpy as np
import random
import math
from PIL import Image, ImageDraw
from lighteffect import LightEffect

from output_image import OutputImage

Angle = float
Polar = Tuple[Angle, float, float]  # angle, dist0, dist1


class Firework(Calc):
    FW_PAUSE = 0
    FW_LAUNCH = 1
    FW_BLOW = 2
    LAUNCH_TIME_PROP = 0.20
    image_processed: Image.Image
    image_drawer: ImageDraw.ImageDraw

    width: int
    height: int
    phase: int
    ray_width: int

    time: float

    min_duration: float
    max_duration: float
    min_pause: float
    max_pause: float

    duration: float

    min_x: int
    max_x: int

    min_y: int
    max_y: int
    start_y: int
    final_x: int  # x coordinate  of explosion
    final_y: int  # y  coordinate of exposion

    min_intensity: float
    max_intensity: float
    intensity: float

    size_amplifier: float

    colors: List[Tuple[int, int, int]]
    color: Tuple[int, int, int]
    rays: List[Angle]

    launch_curve_d0: Curve
    launch_curve_d1: Curve
    blow_curve_d0: Curve
    blow_curve_d1: Curve

    lumiere: LightEffect
    intensity_curve: Curve
    flickering: float

    def __init__(
        self,
        colors: str,
        x_stat: str = "",
        y_stat: str = "",
        pause: str = "",
        duration: str = "",
        intensity: str = "",
        ray_width: int = 5,
        coords: Tuple[int, int] = (0, 0),
        name_effect: str = None,
        size_amplifier: float = 1.0,
        flickering: float = 1.0,
        master=None,
    ) -> None:
        super().__init__(coords=coords, master=master)
        self.image_processed = None
        self.image_drawer = None
        self.color = None
        self.width = None
        self.height = None
        self.ray_width = int(ray_width)
        self.size_amplifier = float(size_amplifier)
        self.lumiere = LightEffect(intensity=0)
        if name_effect is not None and master is not None:
            self.master.add_named_effect(name_effect, self.lumiere)

        self.min_x, self.max_x = map(int, x_stat.split(","))
        self.min_y, self.max_y, self.start_y = map(int, y_stat.split(","))
        self.min_duration, self.max_duration = map(float, duration.split(","))
        self.min_intensity, self.max_intensity = map(float, intensity.split(","))
        self.min_pause, self.max_pause = map(float, pause.split(","))

        if colors == "all":
            self.colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0)] + [
                tuple(c) for c in np.random.randint(0, 255, size=(30, 3))
            ]
            self.colors = [(r, g, b, 255) for (r, g, b) in self.colors]
        else:
            colors = [tuple(map(int, c.split(","))) for c in colors.split(";")]
            self.colors = []
            for c in colors:
                if len(c) == 3:
                    self.colors.append(c + (255,))
                elif len(c) == 4:
                    self.colors.append(c)
                else:
                    raise Exception(f"Invalid color read {c}")
        self.enter_phase(self.FW_PAUSE)

        self.launch_curve_d0 = LinearCurve(a=-0.8, b=1)
        self.launch_curve_d1 = CappedCurve(LinearCurve(a=-1, b=1), mini=0)

        self.blow_curve_d0 = LinearCurve(a=1)
        self.blow_curve_d1 = CappedCurve(LinearCurve(a=0.85, b=0.15), maxi=1)

        degree = 5
        poly = [-1] + [0 for _ in range(degree - 2)] + [1]
        self.first_intensity_curve = PolynomCurve(poly)
        xP4 = (
            self.first_intensity_curve
        )  # ComposedCurve(QuadraticCurve(a=-0.85, b=0.8), self.first_intensity_curve)
        flickering = float(flickering)
        ondulation = SinCurve(
            7 * np.math.pi,
            ampl=0.02 * flickering,
            phase=np.math.pi / 2,
            dec=1 - 0.025 * flickering,
        )
        curve = MulCurve(xP4, ondulation)
        self.intensity_curve = CappedCurve(curve, 0, 1)

        master.add_size_listener(self)

    def set_dim(self, width: int, height: int):
        self.width = width  # // 2
        self.height = height  # // 2
        self.image_processed = Image.new("RGBA", (self.width * 2, self.height * 2))
        self.image_drawer = ImageDraw.ImageDraw(self.image_processed, mode="RGBA")
        self.lumiere.set_dist(np.math.sqrt(self.width ** 2 + self.height ** 2))

    def enter_phase(self, phase: int):
        if phase == self.FW_PAUSE:
            self.enter_pause()
        elif phase == self.FW_BLOW:
            self.enter_blow()
        elif phase == self.FW_LAUNCH:
            self.enter_launch()
        else:
            raise Exception("Trying to go in unexpected phase")

    def enter_pause(self):
        self.phase = self.FW_PAUSE

        self.time = 0
        self.duration = (
            random.random() * (self.max_pause - self.min_pause) + self.min_pause
        )
        self.lumiere.set_intensity(0)

    def enter_launch(self):
        self.phase = self.FW_LAUNCH

        self.time = 0
        self.duration = (
            random.random() * (self.max_duration - self.max_duration)
            + self.min_duration
        )
        self.intensity = (
            random.random() * (self.max_intensity - self.min_intensity)
            + self.min_intensity
        )
        color = random.choice(self.colors)
        while color == self.color:
            color = random.choice(self.colors)
        self.color = color
        self.final_x = 2 * random.randint(self.min_x, self.max_x)
        self.final_y = 2 * random.randint(self.min_y, self.max_y)

        self.lumiere.set_color(self.color)
        color_coeff_s = (self.intensity) / (self.max_intensity + self.min_intensity)
        color_coeff_v = color_coeff_s * self.intensity / self.max_intensity
        t, s, v = self.lumiere.color_tsv
        self.lumiere.color_tsv = (
            t,
            s * color_coeff_s,
            v * color_coeff_v,
        )
        self.lumiere.set_coords((self.final_x / 2, self.final_y / 2))

        self.ref_dist = abs(self.final_y - self.start_y * 2)
        alpha = math.pi / 2

        self.rays = [alpha]

    def enter_blow(self):
        self.phase = self.FW_BLOW

        self.time = 0
        self.ref_dist = 0.2 * self.ref_dist * self.intensity * self.size_amplifier
        nb_step = 6
        self.rays.clear()
        step = 2 * math.pi / nb_step
        alpha = random.random() * 2 * math.pi
        for i in range(nb_step):
            self.rays.append(alpha)
            alpha += step

    def compute(self, output: Union[str, OutputImage]):
        if self.image_processed is None:
            raise Exception("Firework not ready to launch (size not given)")
        self.time += Calc.TIMESTEP
        if self.phase == self.FW_PAUSE:
            self.compute_pause()
        elif self.phase == self.FW_LAUNCH:
            self.compute_launch(output)
        elif self.phase == self.FW_BLOW:
            self.compute_blow(output)
        else:
            raise Exception("Trying to compute an unexpected phase")

    def compute_pause(self):
        if self.time > self.duration:
            self.enter_phase(self.FW_LAUNCH)

    def compute_blow(self, output: Union[str, OutputImage]):
        if self.time > self.duration * (1 - self.LAUNCH_TIME_PROP):
            self.enter_phase(self.FW_PAUSE)
            return
        self.image_processed.paste(
            (0, 0, 0, 0), (0, 0, self.width * 2, self.height * 2)
        )  # clear image

        t = self.time / (self.duration * (1 - self.LAUNCH_TIME_PROP))
        self.lumiere.set_intensity(self.intensity_curve.calc(t) * self.intensity)
        for ray in self.rays:
            d0 = self.blow_curve_d0.calc(t) * self.ref_dist
            d1 = self.blow_curve_d1.calc(t) * self.ref_dist
            x0, y0 = (
                d0 * math.cos(ray) + self.final_x,
                d0 * math.sin(ray) + self.final_y,
            )
            x1, y1 = (
                d1 * math.cos(ray) + self.final_x,
                d1 * math.sin(ray) + self.final_y,
            )
            self.image_drawer.line(
                (x0, y0, x1, y1), fill=self.color, width=self.ray_width
            )

        self.out_buffer = np.array(
            # self.image_processed
            self.image_processed.resize(
                (self.width, self.height), resample=Image.ANTIALIAS
            ).convert("RGBA")
        ).astype(np.float32)
        self.apply_effects()
        if type(output) == str:
            self.save_as(output)
        else:
            self.out_buffer[:, :, 3] /= 255
            output.paste_on(self)

    def compute_launch(self, output: Union[str, OutputImage]):
        if self.time > self.duration * self.LAUNCH_TIME_PROP:
            self.enter_phase(self.FW_BLOW)
            return
        self.image_processed.paste(
            (0, 0, 0, 0), (0, 0, self.width * 2, self.height * 2)
        )  # clear image

        t = self.time / (self.duration * self.LAUNCH_TIME_PROP)
        ray = self.rays[0]
        d0 = self.launch_curve_d0.calc(t) * self.ref_dist
        d1 = self.launch_curve_d1.calc(t) * self.ref_dist
        x0, y0 = self.final_x, d0 * math.sin(ray) + self.final_y
        x1, y1 = self.final_x, d1 * math.sin(ray) + self.final_y
        self.image_drawer.line((x0, y0, x1, y1), fill=self.color, width=self.ray_width)

        self.out_buffer = np.array(
            # self.image_processed
            self.image_processed.resize(
                (self.width, self.height), resample=Image.ANTIALIAS
            ).convert("RGBA")
        ).astype(np.float32)
        self.apply_effects()
        if type(output) == str:
            self.save_as(output)
        else:
            self.out_buffer[:, :, 3] /= 255
            output.paste_on(self)

    def reset(self):
        self.enter_phase(self.FW_PAUSE)
