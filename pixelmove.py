import numpy as np
import random
from calc import Calc
import effect

Effect = effect.Effect


class PixelMove(Effect):
    square_size: int
    displace_probability: float
    area_covered: float

    def __init__(
        self,
        square_size: int = 1,
        displace_probability: float = 0.3,
        area_covered: float = 0.4,
    ) -> None:
        super().__init__()
        self.square_size = square_size
        self.displace_probability = displace_probability
        self.area_covered = area_covered

    def apply(self, other: Calc):
        width, height = other.width, other.height
        dimension = width * height // self.square_size
        positions = (
            (random.randrange(width), random.randrange(height))
            for _ in range(dimension)
        )
        for (x, y) in positions:
            if not np.any(
                other.out_buffer[x : x + self.square_size, y : y + self.square_size, 3]
                < 0.01
            ):
                if random.random() < self.displace_probability:
                    vx, vy = random.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
                    nx, ny = x + vx, y + vy
                    other.out_buffer[
                        nx : nx + self.square_size, ny : ny + self.square_size
                    ] = other.out_buffer[
                        x : x + self.square_size, y : y + self.square_size
                    ]
