import numpy as np
import calc


class Effect:
    def apply(self, other: "calc.Calc"):
        raise NotImplementedError
