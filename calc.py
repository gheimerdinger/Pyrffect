from typing import Sequence, Tuple, Union
import numpy as np
from PIL import Image
import effect
import output_image

Master_ = Union["Pyrffect", None]


class Calc:
    buffer: np.ndarray
    out_buffer: np.ndarray
    effects: Sequence[effect.Effect] = []
    width: int
    height: int
    coords: Tuple[int, int]
    TIMESTEP: float = 0.033
    master: Master_

    @staticmethod
    def set_timestep(timestep):
        Calc.TIMESTEP = timestep

    def __init__(self, coords=(0, 0), master: Master_ = None):
        self.buffer = None
        self.effects = []
        self.coords = coords
        self.master = master

    def set_dim(self, width: int, height: int):
        raise Exception("The dimension of a normal Calc are fixed")

    def reset(self):
        pass

    def add_effect(self, effect: effect.Effect):
        self.effects.append(effect)

    def apply_effects(self):
        for e in self.effects:
            e.apply(self)

    def compute(self, output: Union[str, output_image.OutputImage]):
        self.apply_effects()
        if type(output) is str:
            self.save_as(output)
        else:
            output.paste_on(self)

    def save_as(self, name: str):
        out = (self.out_buffer * np.array([1, 1, 1, 255])).astype(np.uint8)
        img = Image.fromarray(out, mode="RGBA")
        img.save(name)
