import os
import sys
from calc import Calc
from firework import Firework
from fusion_mode import FusionMode
from fusion_linear import FusionLinear
from lighteffect import LightEffect
from pixelmove import PixelMove
from pyrffects import Pyrffect
from flat import Flat
import xml.etree.ElementTree as Et
import getopt

effects = {
    "pixel": PixelMove,
    "light": LightEffect,
}

calc_types = {
    "calc": Calc,
    "firework": Firework,
    "flat": Flat,
}

fusions = {
    "flat": FusionMode,
    "linear": FusionLinear,
}

named_effects = {}


def compare_wh(w, h, x, y, nw, nh):
    if nw is not None:
        nw += x
    if nh is not None:
        nh += y
    if nw is not None and (w is None or (w > 0 and nw > w)):
        w = nw
    if nh is not None and (h is None or (h > 0 and nh > h)):
        h = nh
    return w, h


def parse_effects(nd: Et.Element, calc: Calc):
    for child_node in nd:
        if child_node.tag not in effects:
            raise Exception("Unknown effect type")
        new_effect = effects[child_node.tag](**child_node.attrib)
        calc.add_effect(new_effect)


def parse_calc(nd: Et.Element, w, h, master=None):
    results_elem = []
    for child_node in nd:
        if child_node.tag not in calc_types:
            raise Exception("Unknown calcs type")
        if calc_types[child_node.tag] is None:
            print(f"{child_node.tag} not implemented yet... Ignored.", file=sys.stderr)
            continue
        x, y = 0, 0
        order = None
        if "x" in child_node.attrib:
            x = int(child_node.attrib["x"])
            child_node.attrib.pop("x")
        if "y" in child_node.attrib:
            y = int(child_node.attrib["y"])
            child_node.attrib.pop("y")
        if "order" in child_node.attrib:
            order = child_node.attrib["order"]
            child_node.attrib.pop("order")
        new_calc = calc_types[child_node.tag](
            master=master, coords=(x, y), **child_node.attrib
        )
        w, h = compare_wh(w, h, x, y, new_calc.width, new_calc.height)
        parse_effects(child_node, new_calc)

        results_elem.append((new_calc, order))
    return results_elem, w, h


if __name__ == "__main__":
    DEBUG = True
    if len(sys.argv) < 2:
        print("No file given", file=sys.stderr)
        sys.exit(2)
    filename = sys.argv[1]
    print(f"Reading {filename}")
    tree = Et.parse(filename)

    root = tree.getroot()
    if root.tag != "Pyrffect":
        print("This is not a pyrffect XML.", file=sys.stderr)
        sys.exit(2)
    w, h = None, None
    if "width" in root.attrib:
        w = -int(root.attrib["width"])
    if "height" in root.attrib:
        h = -int(root.attrib["height"])
    p = Pyrffect("OUT", "img{}.png")

    try:
        calcs, w, h = parse_calc(root, w, h, master=p)
    except Exception as e:
        if DEBUG:
            raise e
        print(e, file=sys.stderr)
        sys.exit(1)

    w = 0 if w is None else w
    h = 0 if h is None else h
    w, h = abs(w), abs(h)
    if not os.path.exists("OUT"):
        os.mkdir("OUT")
    print(w, h)
    p.set_dim(w, h)
    if "fusion_mode" in root.attrib:
        fusion = root.attrib["fusion_mode"]
        if fusion not in fusions:
            print("No corresponding fusion mode", file=sys.stderr)
            sys.exit(2)
        p.set_fusionmode(fusions[fusion]())

    for c, order in calcs:
        p.add_calc(c, order)

    framerate = 60
    duration = 10
    if "duration" in root.attrib:
        duration = int(root.attrib["duration"])
    if "framerate" in root.attrib:
        framerate = int(root.attrib["framerate"])

    opts, args = getopt.getopt(
        sys.argv[2:],
        "f:d:",
        ["duration=", "framerate="],
    )
    for o, a in zip(opts, args):
        print(o, a)
        if o in ("-f", "--framerate"):
            framerate = int(a)
        elif o in ("-d", "--duration"):
            duration = int(a)

    try:
        p.compute(duration * framerate)
    except KeyboardInterrupt:
        print("Only part of the images were generated")
        if p.last_valid is None:
            print("No valid images were created, stopping", file=sys.stderr)
            sys.exit(2)
        invalid_file = (
            f"{p.output_directory}/{p.output_fileformat.format(p.last_valid + 1)}"
        )
        if os.path.exists(invalid_file):
            os.remove(invalid_file)

    if "out" in root.attrib:
        command = f"ffmpeg -r 30 -f image2 -i OUT/img%d.png -vcodec libx264 -crf 25 {root.attrib['out']}"
        os.system(command)

    if "remove" in root.attrib and root.attrib["remove"] in ("true", "t", "1"):
        os.system("rm OUT/img*.png")
