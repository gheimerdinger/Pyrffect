from typing import List, Tuple, Union

from numpy.core.fromnumeric import shape
from calc import Calc
import numpy as np
from PIL import Image, ImageDraw

from output_image import OutputImage

Polar = Tuple[float, float, float]


class Firework(Calc):
    FW_PAUSE = 0
    FW_BLOW = 1
    LAUNCH_TIME_PROP = 0.05
    image_processed: Image.Image
    image_drawer: ImageDraw.ImageDraw

    width: int
    height: int
    phase: int

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

    min_intensity: float
    max_intensity: float
    intensity: float

    colors: List[Tuple[int, int, int]]
    color: Tuple[int, int, int]
    rays: List[Polar]

    def __init__(
        self,
        colors: str,
        x_stat: str = "",
        y_stat: str = "",
        pause: str = "",
        duration: str = "",
        intensity: str = "",
        master=None,
    ) -> None:
        self.image_processed = None
        self.image_drawer = None
        self.color = None

        self.min_x, self.max_x = map(int, x_stat.split(","))
        self.min_y, self.max_y, self.start_y = map(int, y_stat.split(","))
        self.min_duration, self.max_duration = map(float, duration.split(","))
        self.min_intensity, self.max_intensity = map(float, intensity.split(","))
        self.min_pause, self.max_pause = map(float, pause.split(","))

        if colors == "all":
            self.colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0)] + [
                np.random.randint(0, 255, shape=(30, 3))
            ]
        else:
            self.colors = [tuple(map(int, c.split(","))) for c in colors.split(";")]
        self.enter_phase(self.FK_PAUSE)

        master.add_size_listener(self)  # TODO Ajouter listener de propriété

    def set_dim(self, width: int, height: int):
        self.width = width
        self.height = height
        self.image_processed = Image.new("RGBA", (self.width * 2, self.height * 2))
        self.image_drawer = ImageDraw.ImageDraw(self.image_processed)

    def enter_phase(self, phase: int):
        if phase == self.FW_PAUSE:
            self.enter_pause()
        elif phase == self.FW_BLOW:
            self.enter_blow()
        else:
            raise Exception("Trying to go in unexpected phase")

    def enter_pause(self):
        self.phase = self.FW_PAUSE

    def enter_blow(self):
        self.phase = self.FW_BLOW

    def compute(self, output: Union[str, OutputImage]):
        if self.image_processed is None:
            raise Exception("Firework not ready to launch (size not given)")
        self.time += Calc.TIMESTEP
        if self.phase == self.FW_PAUSE:
            self.compute_pause()
        elif self.phase == self.FW_BLOW:
            self.compute_blow(output)
        else:
            raise Exception("Trying to compute an unexpected phase")

    def compute_pause(self):
        if self.time > self.duration:
            self.enter_phase(self.FW_BLOW)

    def compute_blow(self, output: Union[str, OutputImage]):
        if self.time > self.duration:
            # TODO put density to 0
            self.enter_phase(self.FW_BLOW)
            return
        self.image_processed.paste((0, 0, 0, 0), (0, 0, self.width, self.height))
        if len(self.rays) == 1:
            ray = self.rays[0]
            t = self.time() / (self.duration * self.LAUNCH_TIME_PROP)
            if t > 1:
                # TODO Add rays + put intensity to effect
                pass
            else:
                # TODO Advance current ray
                pass
        else:
            # TODO decrease intensity of effect
            for ray in self.rays:
                # TODO Advance ray
                pass

        if type(output) == str:
            self.save_as(output)
        else:
            output.paste_on(
                np.array(
                    self.image_processed.resize(
                        (self.width, self.height), resample=Image.LANCZOS
                    ).convert("RGBA")
                )
            )

    def open(self, filename: str):
        pass

    def reset(self):
        self.enter_phase(self.FW_PAUSE)

    def save_as(self, name: str):
        self.image_processed.resize(
            (self.width, self.height), resample=Image.LANCZOS
        ).save(name)
