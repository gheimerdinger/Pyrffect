import os
import sys
from calc import Calc
from fusion_mode import FusionMode
from fusion_linear import FusionLinear
from pixelmove import PixelMove
from pyrffects import Pyrffect
import xml.etree.ElementTree as Et
import getopt

effects = {
    "pixel": PixelMove,
}

calc_types = {
    "calc": Calc,
    "firework": None,
}

fusions = {
    "flat": FusionMode,
    "linear": FusionLinear,
}

named_effects = {}


def compare_wh(w, h, nw, nh):
    if w is None or (w > 0 and nw > w):
        w = nw
    if h is None or (h > 0 and nh > h):
        h = nh
    return w, h


def parse_effects(nd: Et.Element, calc: Calc):
    for child_node in nd:
        if child_node.tag not in effects:
            raise Exception("Unknown effect type")
        new_effect = effects[child_node.tag](**child_node.attrib)
        calc.add_effect(new_effect)


def parse_calc(nd: Et.Element, w, h):
    results_elem = []
    for child_node in nd:
        if child_node.tag not in calc_types:
            raise Exception("Unknown calcs type")
        if calc_types[child_node.tag] is None:
            print(f"{child_node.tag} not implemented yet... Ignored.", file=sys.stderr)
            continue
        x, y = 0, 0
        order = None
        pos = {}
        if "x" in child_node.attrib:
            pos["x"] = int(child_node.attrib["x"])
            child_node.attrib.pop("x")
        if "y" in child_node.attrib:
            pos["y"] = int(child_node.attrib["y"])
            child_node.attrib.pop("y")
        if "order" in child_node.attrib:
            order = child_node.attrib["order"]
            child_node.attrib.pop("order")
        new_calc = calc_types[child_node.tag](**child_node.attrib)
        w, h = compare_wh(w, h, x + new_calc.width, y + new_calc.height)
        parse_effects(child_node, new_calc)

        results_elem.append((new_calc, order, pos))
    return results_elem, w, h


if __name__ == "__main__":
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
        calcs, w, h = parse_calc(root, w, h)
    except Exception as e:
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

    for c, order, pos in calcs:
        p.add_calc(c, order, pos)

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
