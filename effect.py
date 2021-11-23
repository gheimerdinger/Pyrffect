from typing import Iterator
import numpy as np
import calc

Calc = calc.Calc


class Effect:
    def apply(self, other: Calc):
        raise NotImplementedError
