import numpy as np
import random
from calc import Calc
import effect

Effect = effect.Effect


class PixelMove(Effect):
    square_size: int
    displace_probability: float
    area_covered: float
    ticks: int
    period: int

    last_transform: list

    def __init__(
        self,
        square_size: int = 1,
        displace_probability: float = 0.3,
        area_covered: float = 0.4,
        ticks: int = 1,
    ) -> None:
        self.square_size = int(square_size)
        self.displace_probability = float(displace_probability)
        self.area_covered = float(area_covered)
        self.ticks = 0
        self.period = int(ticks)
        self.last_transform = None

    def apply_last_transform(self, other: Calc):
        if self.last_transform is None:
            return
        for (x, y, fx, fy, nx, ny, nfx, nfy) in self.last_transform:
            other.out_buffer[nx:nfx, ny:nfy] = other.out_buffer[x:fx, y:fy]

    def apply(self, other: Calc):
        self.ticks += 1
        if self.ticks < self.period:
            return self.apply_last_transform(other)
        self.last_transform = []
        self.ticks = 0
        width, height, _ = other.out_buffer.shape
        dimension = int(width * height // self.square_size * self.area_covered)
        positions = zip(
            np.random.rand(dimension),
            np.random.randint(0, width - 1, dimension),
            np.random.randint(0, height - 1, dimension),
        )
        for (tirage, x, y) in positions:
            fx = min(width, x + self.square_size)
            fy = min(height, y + self.square_size)
            if tirage < self.displace_probability:
                vx, vy = [(1, 0), (-1, 0), (0, 1), (0, -1)][int(tirage * 1000) % 4]
                nx, ny = x + vx, y + vy
                if nx < 0:
                    nx = 0
                    x += 1
                if ny < 0:
                    ny = 0
                    y += 1
                nfx = min(width, fx + vx)
                nfy = min(height, fy + vy)
                if nfx - nx < fx - x:
                    fx -= 1
                if nfy - ny < fy - y:
                    fy -= 1
                self.last_transform.append((x, y, fx, fy, nx, ny, nfx, nfy))
                other.out_buffer[nx:nfx, ny:nfy] = other.out_buffer[x:fx, y:fy]
