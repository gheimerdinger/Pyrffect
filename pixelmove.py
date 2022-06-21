import numpy as np
import random
from calc import Calc
from multiprocessing import Pool
import effect

Effect = effect.Effect


class PixelMove(Effect):
    square_size: int
    displace_probability: float
    area_covered: float
    ticks: int
    period: int

    last_transform: list
    implementation_clean: bool = True

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

    def move(self, other, x, y, fx, fy, nx, ny, nfx, nfy):
        self.tmp_other.out_buffer[nx:nfx, ny:nfy] = other.out_buffer[x:fx, y:fy]

    def apply_last_transform(self, other: Calc):
        if self.last_transform is None:
            return
        if self.implementation_clean:
            self.apply_clean(other)
        else:
            self.apply_dirty(other)

    def apply_dirty(self, other: Calc):
        mp = Pool(len(self.last_transform))
        self.tmp_other = other
        mp.starmap(self.move, self.last_transform)
        mp.close()

    def apply_clean(self, other: Calc):
        dim = self.last_transform.shape[0]
        self.tmp_other = other
        for i in range(dim):
            x, y, fx, fy, nx, ny, nfx, nfy = self.last_transform[i]
            self.move(other, x, y, fx, fy, nx, ny, nfx, nfy)

    def apply(self, other: Calc):
        self.ticks += 1
        if self.ticks < self.period:
            return self.apply_last_transform(other)
        self.ticks = 0
        width, height, _ = other.out_buffer.shape
        dimension = int(width * height // self.square_size * self.area_covered)
        tirage = np.random.rand(dimension)
        tirage = tirage[tirage < self.displace_probability]
        dimension = tirage.shape[0]
        x, y = [
            np.random.randint(0, width - 1, dimension),
            np.random.randint(0, height - 1, dimension),
        ]
        fx = np.minimum(x + self.square_size, width)
        fy = np.minimum(y + self.square_size, height)
        tirage = ((tirage * 1000) % 4).astype(np.int)
        vx = np.choose(tirage, [1, -1, 0, 0])
        vy = np.choose(tirage, [0, 0, 1, -1])
        nx = x + vx
        ny = y + vy
        x[nx < 0] += 1
        nx[nx < 0] = 0
        y[ny < 0] += 1
        ny[ny < 0] = 0

        nfx = np.minimum(fx + vx, width)
        nfy = np.minimum(fy + vy, height)
        fx[nfx - nx < fx - x] -= 1
        fy[nfy - ny < fy - y] -= 1

        self.last_transform = np.stack((x, y, fx, fy, nx, ny, nfx, nfy), axis=-1)

        return self.apply_last_transform(other)
