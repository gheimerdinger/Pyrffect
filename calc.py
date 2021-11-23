from typing import Any, Iterator
import numpy as np
from PIL import Image
import effect
import output_image

Effect = effect.Effect
OutputImage = output_image.OutputImage 

class Calc:
    buffer: np.ndarray
    out_buffer: np.ndarray
    effects: Iterator(Effect)
    width: int
    height: int

    def __init__(self):
        self.buffer = None
        self.effects = []

    def add_effect(self, effect: Effect):
        self.effects.append(effect)

    def open(self, filename: str):
        self.buffer = np.array(Image.open(filename, mode="rgba"))
        self.out_buffer = np.copy(self.buffer)
        self.width, self.height, _, _ = self.buffer.shape()

    def compute(self, output: Any(str, OutputImage)):
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
        img = Image.new("rgb", (self.width, self.height))
        img.putdata(self.out_buffer.reshape((self.width*self.height*3)))
        img.save(name)
