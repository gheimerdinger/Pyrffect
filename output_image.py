import fusion_mode
import fusion_linear
from typing import Any, Tuple
import numpy as np
from PIL import Image

FusionMode = fusion_linear.FusionMode
FusionLinear = fusion_linear.FusionLinear


class OutputImage:
    buffer: np.ndarray
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

    def paste_on(self, calc: "Calc"):
        buffer = calc.out_buffer
        w, h, _ = buffer.shape
        w, h = min(w, calc.width), min(h, calc.height)
        x, y = calc.coords
        fx, fy = min(self.width, x + w), min(self.height, y + h)
        self.buffer[x:fx, y:fy] = self.fusion_mode.fuse(
            self.buffer[x:fx, y:fy], buffer[:w, :h]
        )

    def reset(self):
        self.buffer.fill(0)

    def save(self, filename):
        out = (self.buffer * np.array([1, 1, 1, 255])).astype(np.uint8)
        img = Image.fromarray(out, mode="RGBA")
        img.save(filename)
