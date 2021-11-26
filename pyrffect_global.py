import numpy as np
from numpy.core.numeric import full


def tsv_to_rgb(buffer):
    alpha = buffer[:, :, 3]
    maxi = np.max(buffer, axis=-1) / 255
    mini = np.min(buffer, axis=-1) / 255

    s = np.full(buffer.shape[:-1], 0)
    s[maxi > 0.001] = 1 - mini / maxi
    v = maxi
    delta = np.divide(
        1,
        maxi - mini,
        out=np.zeros_like(maxi.shape),
        where=np.abs(maxi - mini) > 0.0001,
    )
    t = np.full(buffer.shape[:-1], fill=0)
    t[maxi == buffer[:, :, 1]] = (buffer[:, :, 2] - buffer[:, :, 0]) * delta + 120
    t[maxi == buffer[:, :, 2]] = (buffer[:, :, 0] - buffer[:, :, 1]) * delta + 240
    t[maxi == buffer[:, :, 0]] = (
        (buffer[:, :, 1] - buffer[:, :, 2]) * delta + 360
    ) % 360  # in last so that mini == maxi does 0
    return t, s, v
