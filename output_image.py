import fusion_mode
import fusion_linear
from typing import Any, Tuple
import numpy as np


class OutputImage:
    buffer: np.ndarray
    actual_pos: Tuple(int, int)
    actual_size: Tuple(int, int)
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

    def paste_on(self, buffer: np.ndarray):
        pass
