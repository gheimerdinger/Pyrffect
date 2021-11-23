from os import WIFCONTINUED
import fusion_mode
import fusion_linear
from typing import Any, Tuple
import numpy as np
from PIL import Image

FusionMode = fusion_linear.FusionMode
FusionLinear = fusion_linear.FusionLinear


class OutputImage:
    buffer: np.ndarray
    actual_pos: Tuple[int, int]
    actual_size: Tuple[int, int]
    fusion_mode: FusionMode
    width: int
    height: int

    def __init__(
        self,
        width: int,
        height: int,
        fusion_mode: FusionMode = None,
    ) -> None:
        self.width = width
        self.height = height
        if fusion_mode is None:
            fusion_mode = FusionLinear()
        self.fusion_mode = fusion_mode
        self.buffer = np.full((self.width, self.height, 4), 0)
        self.actual_pos = None
        self.actual_size = None

    def set_coords(self, x=0, y=0, width=None, height=None):
        width = self.width if width is None else width
        height = self.height if height is None else height
        self.actual_size = (width, height)
        self.actual_pos = (x, y)

    def paste_on(self, buffer: np.ndarray):
        if self.actual_pos is None or self.actual_size is None:
            raise Exception("No coordinates were prepared for this paste")
        w, h, _ = buffer.shape
        w, h = min(w, self.actual_size[0]), min(h, self.actual_size[1])
        x, y = self.actual_pos
        fx, fy = min(self.width, x + w), min(self.height, y + h)
        self.buffer[x:fx, y:fy] = self.fusion_mode.fuse(
            self.buffer[x:fx, y:fy], buffer[:w, :h]
        )

        self.actual_pos = None
        self.actual_size = None

    def prepare_paste(self, pos: Tuple[int, int], size: Tuple[int, int]):
        self.actual_size = size
        self.actual_pos = pos

    def reset(self):
        self.buffer.fill(0)

    def save(self, filename):
        out = (self.buffer * np.array([1, 1, 1, 255])).astype(np.uint8)
        img = Image.fromarray(out, mode="RGBA")
        img.save(filename)
