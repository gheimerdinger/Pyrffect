from typing import Any, Dict, List, Tuple
from calc import Calc
from output_image import OutputImage
from effect import Effect
from fusion_linear import FusionMode

CalcPos = Dict[str, int]
Couche = Tuple[int, Calc]


class Pyrffect:
    calcs: Dict[str, Couche]

    calc_seq: int

    output_directory: str
    output_fileformat: str

    fusion_mode: FusionMode

    width: int
    height: int
    last_valid: int

    size_listener: List[Calc]
    named_effect: Dict[str, Effect]

    def __init__(
        self,
        output_directory: str,
        output_fileformat: str,
        width: int = None,
        height: int = None,
    ):
        self.calcs = {}
        self.calc_seq = 0
        self.output_directory = output_directory
        self.output_fileformat = output_fileformat
        self.fusion_mode = None
        self.width = width
        self.height = height
        self.last_valid = None
        self.size_listener = []
        self.named_effect = {}

    def add_named_effect(self, name: str, effect: Effect):
        if name not in self.named_effect:
            self.named_effect[name] = effect
        else:
            raise Exception(f"Name '{name}' already attributed to another effect.")

    def get_named_effect(self, name: str):
        if name not in self.named_effect:
            raise Exception(f"No named effect have '{name}' for name")
        return self.named_effect[name]

    def add_calc(self, calc, order: int = None):
        if order is None:
            order = self.calc_seq
        self.calcs[self.calc_seq] = (order, calc)
        self.calc_seq += 1
        return self.calc_seq - 1

    def add_effect(self, index: int, effect: Effect):
        if index not in self.calcs:
            raise Exception("Undefined calc")
        self.calcs[index][1].add_effect(effect)

    def add_size_listener(self, calc: Calc):
        self.size_listener.append(calc)
        if self.width is not None and self.height is not None:
            calc.set_dim(self.width, self.height)

    def set_dim(self, width: int, height: int):
        self.width = width
        self.height = height
        for listen_size in self.size_listener:
            listen_size.set_dim(width, height)

    def set_fusionmode(self, fusion_mode: FusionMode):
        self.fusion_mode = fusion_mode

    def _fuse(self) -> List[Calc]:
        def fusion(l0, l1):
            result = []
            i, j = 0, 0
            s0, s1 = len(l0), len(l1)
            while i < s0 and j < s1:
                if l0[i] < l1[j]:
                    result.append(l0[i])
                    i += 1
                else:
                    result.append(l1[j])
                    j += 1
            while i < s0:
                result.append(l0[i])
            while j < s1:
                result.append(l1[j])
                j += 1
            return result

        def split(l):
            if len(l) > 1:
                mid = len(l) // 2
                return fusion(split(l[:mid]), split(l[mid:]))
            else:
                return l

        calcs = [self.calcs[key] for key in self.calcs]

        return [(e) for (_, e) in split(calcs)]

    def compute(self, out: str, framerate: int, frame: int):
        if self.width is None or self.height is None:
            raise Exception("No valid dimension to compite the pyrffect.")
        output_result = OutputImage(self.width, self.height, framerate, out, self.fusion_mode)
        orderer_calc = self._fuse()
        for c in orderer_calc:
            c.reset()
        self.last_valid = None
        for i in range(frame):
            filename = (self.output_directory + "/" + self.output_fileformat).format(i)
            for c in orderer_calc:
                c.compute(output_result)
            output_result.save(i+1, frame)
            output_result.reset()
            self.last_valid = i
