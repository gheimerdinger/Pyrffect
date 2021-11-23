from typing import Any, Iterator, Union
import numpy as np
from PIL import Image
import effect
import output_image


class Calc:
    buffer: np.ndarray
    out_buffer: np.ndarray
    effects: Iterator[effect.Effect]
    width: int
    height: int
    TIMESTEP: float = 0.33

    @staticmethod
    def set_timestep(timestep):
        Calc.TIMESTEP = timestep

    def __init__(self, filename: str = None, master=None):
        self.buffer = None
        self.effects = []
        if filename is not None:
            self.open(filename)

    def set_dim(self, width: int, height: int):
        raise Exception("The dimension of a normal Calc are fixed")

    def reset(self):
        pass

    def add_effect(self, effect: effect.Effect):
        self.effects.append(effect)

    def open(self, filename: str):
        img = Image.open(filename)
        img = img.convert("RGBA")
        self.buffer = np.array(img).astype(np.float32)
        self.buffer[:, :, 3] /= 255.0
        print(self.buffer.dtype)
        self.out_buffer = np.copy(self.buffer)
        self.width, self.height, _ = self.buffer.shape
        self.save_as("test.png")

    def compute(self, output: Union[str, output_image.OutputImage]):
        if self.buffer is None:
            raise NotImplementedError
        self.out_buffer[:, :, :] = self.buffer
        for e in self.effects:
            e.apply(self)
        if type(output) is str:
            self.save_as(output)
        else:
            output.paste_on(self.out_buffer)

    def save_as(self, name: str):
        out = (self.out_buffer * np.array([1, 1, 1, 255])).astype(np.uint8)
        img = Image.fromarray(out, mode="RGBA")
        img.save(name)
