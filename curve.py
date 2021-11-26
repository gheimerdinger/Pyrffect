import os
from tkinter import Widget
from typing import List, Tuple, Union
from PIL.Image import TRANSPOSE
import numpy as np
import datetime


class Curve:
    def calc(self, t):
        raise NotImplementedError


class LinearCurve(Curve):
    a: float  # coefficient directeur
    b: float  # ordonnée à l'origine

    def __init__(self, a: float = 1, b: float = 0):
        self.a = a
        self.b = b

    def calc(self, t):
        return self.a * t + self.b


class CappedCurve(Curve):
    child_curve: Curve
    mini: float
    maxi: float

    def __init__(self, curve: Curve, mini: float = None, maxi: float = None):
        self.child_curve = curve
        self.mini = mini
        self.maxi = maxi

    def calc(self, t):
        value = self.child_curve.calc(t)
        if type(t) == float:
            if self.maxi is not None and value > self.maxi:
                value = self.maxi
            if self.mini is not None and value < self.mini:
                value = self.mini
        else:
            if self.maxi is not None:
                value[value > self.maxi] = self.maxi
            if self.mini is not None:
                value[value < self.mini] = self.mini
        return value


class QuadraticCurve(Curve):
    a: float
    b: float
    c: float

    def __init__(self, a: float = 1, b: float = 1, c: float = 1):
        self.a = a
        self.b = b
        self.c = c

    def calc(self, t):
        return t * (self.a * t + self.b) + self.c


class PolynomCurve(Curve):
    coefficients: List[float]

    def __init__(self, coefficients: Union[List[float], str]) -> None:
        if type(coefficients) is str:
            self.coefficients = [float(c) for c in coefficients.split(",")]
        else:
            self.coefficients = coefficients

    def calc(self, t):
        result = 0
        for c in self.coefficients:
            result *= t
            result += c
        return result


class PolynomPointCurve(Curve):
    control_points: List[Tuple[float, float]]
    true_curve: Curve
    seuil: int

    def __init__(self, control_points: Union[str, List[Tuple[float, float]]], seuil=9):
        if type(control_points) == str:
            self.control_points = [
                tuple([float(c) for c in p.split(",")])
                for p in control_points.split(";")
            ]
        else:
            self.control_points = control_points
        if len(self.control_points) > seuil:
            sorted_control_point = []
            while len(self.control_points) > 0:
                index, value = 0, self.control_points[0][0]
                for i, (v, _) in enumerate(self.control_points):
                    if v < value:
                        value = v
                        index = i
                sorted_control_point.append(self.control_points.pop(index))
            mid_index = len(sorted_control_point) // 2
            mid_val = sorted_control_point[mid_index][0]
            self.true_curve = SplitCurve(
                PolynomPointCurve(sorted_control_point[: mid_index + 1], seuil),
                PolynomPointCurve(sorted_control_point[mid_index:], seuil),
                split_t=mid_val,
            )
        else:
            self.solve_polynome()
        PolynomPointCurve.entete = PolynomPointCurve.entete[:-1]

    def calc(self, t):
        return self.true_curve.calc(t)

    def __str__(self):
        resA = ""
        resB = "["
        for cp in self.control_points:
            resA += f"{cp[0]},{cp[1]};"
            resB += f"({cp[0]}, {cp[1]}), "
        return resA[:-1] + "\n" + resB + "]"

    def solve_polynome(self):
        n = len(self.control_points) - 1
        matrix = [
            np.array([x ** (n - i) for i in range(n + 1)], dtype=np.float64)
            for (x, _) in self.control_points
        ]
        Y = [y for (_, y) in self.control_points]

        matrix, Y = self.pivot(matrix, Y)
        # print("_________________________")
        # for (L, y) in zip(matrix, Y):
        #    print(L, y)
        matrix, Y = self.climb(matrix, Y)
        # print("_________________________")
        # for (L, y) in zip(matrix, Y):
        #    print(L, y)
        self.true_curve = PolynomCurve(Y)

    def pivot(self, L, Y):
        n = len(L)
        p = 0
        while p < n:
            if abs(L[p][p]) < 10e-9:
                found = False
                for k in range(n):
                    if abs(L[k][p]) > 10e-9:
                        found = True
                        break
                if found:
                    Lk = L[k]
                    Yk = Y[k]
                    Lp = L[p]
                    Yp = Y[p]

                    L[p] = Lk
                    L[k] = Lp
                    Y[k] = Yp
                    Y[p] = Yk

                    # switch avec la dernière ligne pour éviter boucle eternel
                    p = n - 1
                    Ln = L[n - 1]
                    Yn = Y[n - 1]
                    Lp = L[p]
                    Yp = Y[p]

                    L[p] = Ln
                    L[n - 1] = Lp
                    Y[k] = Yn
                    Y[n - 1] = Yk
                    if k < p:
                        p = k
                        continue
                else:
                    raise Exception("Problem: impossible to choose a non zero column")
            Lpp = L[p][p]
            L[p] /= Lpp
            Y[p] /= Lpp
            for k in range(p + 1, n):
                if abs(L[k][p]) > 10e-9:
                    Lkp = L[k][p]
                    L[k] -= L[p] * Lkp
                    Y[k] -= Y[p] * Lkp
            p += 1
        return L, Y

    def climb(self, L, Y):
        n = len(L)
        p = n - 1
        while p > 0:
            k = p - 1
            while k >= 0:
                Lkp = L[k][p]
                L[k][p] = 0
                Y[k] -= Lkp * Y[p]
                k -= 1
            p -= 1
        return L, Y


class SplitCurve(Curve):
    curve_a: Curve
    curve_b: Curve
    split_t: float

    def __init__(self, curve_a: Curve, curve_b: Curve, split_t: float = 0) -> None:
        self.curve_a = curve_a
        self.curve_b = curve_b
        self.split_t = split_t

    def calc(self, t):
        if type(t) == float:
            if t > self.split_t:
                return self.curve_b.calc(t)
            else:
                return self.curve_a.calc(t)
        else:
            #! Absolutely not opti, expo with each imbriquation
            value_B = self.curve_b.calc(t)
            value_A = self.curve_a.calc(t)
            value_A[t > self.split_t] = value_B
            return value_A


class BezierCurve(Curve):
    control_points: List[Tuple[float, float]]

    def __init__(self, control_points: Union[List[Tuple[float, float]], str]):
        if type(control_points) == str:
            self.control_points = []
        else:
            self.control_points = control_points


if __name__ == "__main__":
    import tkinter as tk

    class Point:
        TRESHOLD = 2
        master: tk.Canvas

        def __init__(self, master: tk.Canvas, x, y) -> None:
            self.master = master
            self.x = x
            self.y = y

            self.up_l = master.create_line(x, y - 2, x, y - 4)
            self.down_l = master.create_line(x, y + 2, x, y + 4)
            self.left_l = master.create_line(x - 2, y, x - 4, y)
            self.right_l = master.create_line(x + 2, y, x + 4, y)

        def close_to(self, x, y):
            return (x - self.x) ** 2 + (y - self.y) ** 2 < self.TRESHOLD ** 2

        def move(self, x, y):
            self.x = x
            self.y = y
            self.master.coords(self.up_l, x, y - 2, x, y - 4)
            self.master.coords(self.down_l, x, y + 2, x, y + 4)
            self.master.coords(self.left_l, x - 2, y, x - 4, y)
            self.master.coords(self.right_l, x + 2, y, x + 4, y)

        def destroy(self):
            self.master.delete(self.up_l, self.down_l, self.left_l, self.right_l)

    class Tracer(tk.Frame):
        points: List[Point]
        width: int
        height: int
        rewrite: False

        def __init__(self, master, width: int = 400, height: int = 400):
            tk.Frame.__init__(self, master)
            self.width = width
            self.height = height
            self.can_trace = tk.Canvas(self, width=width, height=height, bg="white")
            self.can_trace.bind("<ButtonRelease-1>", self.right_click)
            self.can_trace.bind("<ButtonRelease-3>", self.left_click)

            self.button_clear = tk.Button(self, text="RESET", command=self.reset)
            self.button_calc = tk.Button(self, text="Valid", command=self.draw_curve)

            self.can_trace.grid(row=0, column=0, rowspan=2)
            self.button_clear.grid(row=1, column=1)
            self.button_calc.grid(row=0, column=1)

            self.marge_x = 10
            self.marge_y = 10
            self.points = []
            self.seq_point = 0
            self.curve = None
            self.rewrite = False

            if os.path.exists("log_curve.txt"):
                os.system("cp -f log_curve.txt /tmp/log_curve.txt")
                self.rewrite = True
            self.log = open("log_curve.txt", mode="w")
            self.log.write(f"___________________\n{datetime.datetime.now()}\n")
            on_closing.close_f.append(self.on_close)

        def on_close(self):
            self.log.close()
            if self.rewrite:
                print("yes")
                os.system("cat /tmp/log_curve.txt >> log_curve.txt")

        def left_click(self, event: tk.Event):
            x, y = event.x, event.y
            to_destroy = None
            for i, p in enumerate(self.points):
                if p.close_to(x, y):
                    p.destroy()
                    to_destroy = i
                    break
            if to_destroy is not None:
                self.points.pop(to_destroy)

        def right_click(self, event: tk.Event):
            x, y = event.x, event.y
            if all(map(lambda e: not e.close_to(x, y), self.points)):
                self.points.append(Point(self.can_trace, x, y))

        def reset(self):
            self.clean_curve()
            for p in self.points:
                p.destroy()
            self.points.clear()

        def draw_curve(self):
            if len(self.points) > 1:
                self.clean_curve()
                print("________________________")
                self.curve = PolynomPointCurve([(p.x, p.y) for p in self.points])

                xp, yp = 0, self.curve.calc(0)
                for x in range(1, self.width):
                    y = self.curve.calc(x)
                    self.can_trace.create_line(x, y, xp, yp, tags="curve")
                    xp = x
                    yp = y
                self.log.write(f"{self.curve}\n")

        def clean_curve(self):
            self.can_trace.delete("curve")
            self.curve = None

    fen = tk.Tk()

    def on_closing():
        for f in on_closing.close_f:
            f()
        fen.destroy()

    on_closing.close_f = []
    fen.protocol("WM_DELETE_WINDOW", on_closing)

    trac = Tracer(fen)
    trac.pack()

    try:
        fen.mainloop()
    except KeyboardInterrupt:
        on_closing()
