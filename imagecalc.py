from typing import Coroutine, Tuple, Union

from PIL import Image
import numpy as np
from calc import Calc
from output_image import OutputImage


class ImageCalc(Calc):
    def __init__(self, filename: str = None, coords=(0, 0), master=None):
        super().__init__(coords=coords, master=master)
        if filename is not None:
            self.open(filename)

    def compute(self, output: Union[str, OutputImage]):
        if self.buffer is None:
            raise NotImplementedError
        self.out_buffer[:, :, :] = self.buffer
        return super().compute(output)

    def open(self, filename: str):
        img = Image.open(filename)
        img = img.convert("RGBA")
        self.buffer = np.array(img).astype(np.float32)
        self.buffer[:, :, 3] /= 255.0
        self.out_buffer = np.copy(self.buffer)
        self.height, self.width, _ = self.buffer.shape
