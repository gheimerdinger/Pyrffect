from typing import Tuple, Union
from calc import Calc
import numpy as np

from output_image import OutputImage

ColorF_ = Tuple[float, float, float, float]


class Flat(Calc):
    color: ColorF_
    listen_size: bool

    def __init__(
        self,
        width: int = None,
        height: int = None,
        color: ColorF_ = (255, 255, 255, 1.0),
        coords=(0, 0),
        master=None,
    ):
        self.color = color
        self.width = width
        self.height = height
        self.coords = coords
        self.listen_size = False
        if self.width is None or self.height is None:
            self.listen_size = True
            master.add_size_listener(self)
        else:
            self.out_buffer = np.full(
                (self.width, self.height, 4), self.color, dtype=np.float32
            )
        self.buffer = None
        self.master = master

    def set_dim(self, width, height, event=True):
        self.width = width
        self.height = height
        self.out_buffer = np.full(
            (self.width, self.height, 4), self.color, dtype=np.float32
        )

    def stop_listen(self):
        if self.listen_size:
            self.master.remove_size_listener(self)
            self.listen_size = False

    def compute(self, output: Union[str, OutputImage]):
        if self.out_buffer is None:
            raise Exception("Flat surface was never given a size to be displayed")
        if type(output) == str:
            self.save_as(output)
        else:
            output.paste_on(self)
