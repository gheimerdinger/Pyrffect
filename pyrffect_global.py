from PIL import Image
import numpy as np



def rgb_to_tsv(buffer):
    alpha = buffer[:, :, 3]
    # buffer = buffer / 255.0  # tmp
    maxi = np.max(buffer[:, :, :3], axis=-1)
    mini = np.min(buffer[:, :, :3], axis=-1)

    s = np.full(buffer.shape[:-1], 0, dtype=np.float32)

    mask = maxi > 0.0001
    with np.errstate(divide='ignore', invalid='ignore'):
        s[mask] = (1 - mini / maxi)[mask]
    v = maxi / 255
    delta = np.divide(
        np.full(maxi.shape, 60, dtype=np.float32),
        (maxi - mini),
        out=np.full(maxi.shape, 0, dtype=np.float32),
        where=np.abs(maxi - mini) > 0.25,
    )

    t = np.full(buffer.shape[:-1], 0, dtype=np.float32)

    # non_mask = np.logical_not(np.isclose(mini, maxi))

    mask = np.isclose(maxi, buffer[:, :, 1])
    # mask = np.logical_and(np.isclose(maxi, buffer[:, :, 1]), non_mask)
    t[mask] = ((buffer[:, :, 2] - buffer[:, :, 0]) * delta + 120)[mask]
    mg = mask

    mask = np.isclose(maxi, buffer[:, :, 2])
    # mask = np.logical_and(np.isclose(maxi, buffer[:, :, 2]), non_mask)
    t[mask] = ((buffer[:, :, 0] - buffer[:, :, 1]) * delta + 240)[mask]
    mb = mask

    mask = np.isclose(maxi, buffer[:, :, 0])
    # mask = np.logical_and(np.isclose(maxi, buffer[:, :, 0]), non_mask)
    t[mask] = (((buffer[:, :, 1] - buffer[:, :, 2]) * delta + 360) % 360)[
        mask
    ]  # in last so that mini == maxi does 0
    return t, s, v, alpha


def tsv_to_rgb(t, s, v, alpha):
    t_i = (t / 60).astype(np.int) % 6
    f = t / 60 - t_i
    l = v * (1 - s)
    m = v * (1 - f * s)
    n = v * (1 - (1 - f) * s)
    # print(f.dtype, l.dtype, m.dtype, n.dtype, v.dtype, t_i.dtype)
    r = np.choose(t_i, [v, m, l, l, n, v]) * 255
    g = np.choose(t_i, [n, v, v, m, l, l]) * 255
    b = np.choose(t_i, [l, l, n, v, v, m]) * 255
    # print(np.max(r), np.max(g), np.max(b))
    # print(np.min(r), np.min(g), np.min(b))
    return np.stack((r, g, b, alpha), axis=-1)


if __name__ == "__main__":
    import tkinter as tk
    from PIL import ImageTk

    class Vizualizer(tk.Frame):
        def __init__(self, master):
            tk.Frame.__init__(self, master, bg="#23AAF2")

            self.width = 400
            self.height = 400
            self.canvas_show = tk.Canvas(self, width=self.width, height=self.height)
            self.id_img = self.canvas_show.create_image(0, 0, anchor="nw")

            self.cmd = tk.StringVar()
            self.entry_cmd = tk.Entry(
                self, textvariable=self.cmd, bg="#086DAA", fg="#EFEFEF"
            )

            self.msg = tk.StringVar()
            self.msg.set("> ")
            self.lab_message = tk.Label(
                self, textvariable=self.msg, justify="left", bg="#007FCE", anchor="w"
            )

            self.columnconfigure(0, weight=1)

            self.entry_cmd.bind("<Return>", self.compute_cmd)
            self.entry_cmd.bind("<Up>", self.decrease_cmd)
            self.entry_cmd.bind("Down", self.increase_cmd)

            self.canvas_show.grid(row=0, column=0)
            self.entry_cmd.grid(row=1, column=0, sticky=tk.W + tk.E)
            self.lab_message.grid(row=2, column=0, sticky=tk.W + tk.E)

            self.buffer_image = None
            self.tsv_image = None
            self.image = None
            self.tk_image = None

            self.memory_cmd = ["load(cone.png)"]
            self.index_cmd = 1

            self.func = {
                "load": (self.load, 1),
                "save": (self.save, 1),
                "rotate": (self.rotate, 1),
                "flat": (self.flat, 3),
            }

        def flat(self, r, g, b):
            r, g, b = [float(e) for e in (r, g, b)]
            self.buffer_image = np.full(
                (self.height, self.width, 4), [r, g, b, 1.0], dtype=np.float32
            )
            self.tsv_image = rgb_to_tsv(self.buffer_image)
            self.update()

        def rotate(self, angle):
            angle = float(angle)
            t = self.tsv_image[0]
            t += angle
            t %= 360

            self.buffer_image = tsv_to_rgb(*self.tsv_image)
            self.update()

        def load(self, filename):
            try:
                self.image = Image.open(filename).convert("RGBA")
            except Exception as e:
                self.buffer_image = None
                self.tsv_image = None
                self.image = None
                self.tk_image = None
                self.canvas_show.itemconfig(self.id_img, image=self.tk_image)
                self.message("Error while loading : " + str(e))
            else:
                self.buffer_image = np.array(self.image).astype(np.float32)
                self.buffer_image[:, :, 3] /= 255
                self.width, self.height = self.image.size
                self.tsv_image = rgb_to_tsv(self.buffer_image)
                self.buffer_image = tsv_to_rgb(*self.tsv_image)
                self.canvas_show.config(width=self.width, height=self.height)
                self.update()

        def save(self, filename):
            if self.image is None:
                return
            try:
                self.image.save(filename)
            except Exception as e:
                self.message("Error while reading : " + str(tk.E))

        def message(self, text):
            self.msg.set("> " + text)

        def compute_cmd(self, ev=None):
            cmd = self.cmd.get()
            if cmd == "":
                return
            self.cmd.set("")
            self.memory_cmd.append(cmd)
            self.index_cmd = len(self.memory_cmd)

            ms = len(cmd)
            header = 0
            while header < ms and cmd[header] != "(":
                header += 1
            cmd_name = cmd[:header]
            if cmd_name in self.func:
                func, n_arg = self.func[cmd_name]
            else:
                return self.message("Wrong function name")

            args = []
            prec_act = header + 1
            act = header + 1
            while act < ms and cmd[act] != ")":
                if cmd[act] == ",":
                    args.append(cmd[prec_act:act])
                    prec_act = act + 1
                    act = act + 1
                else:
                    act += 1
            if prec_act != act:
                args.append(cmd[prec_act:act])
            if len(args) != n_arg:
                return self.message("Number of argument incomplete")
            else:
                func(*args)

        def update(self):
            true_image_buffer = (self.buffer_image * np.array([1, 1, 1, 255])).astype(
                np.uint8
            )
            self.image = Image.fromarray(true_image_buffer)
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas_show.itemconfig(self.id_img, image=self.tk_image)

        def increase_cmd(self, ev=None):
            self.index_cmd = (self.index_cmd + 1) % (len(self.memory_cmd) + 1)
            if self.index_cmd < len(self.memory_cmd):
                self.cmd.set(self.memory_cmd[self.index_cmd])

        def decrease_cmd(self, ev=None):
            self.index_cmd = (self.index_cmd - 1) % (len(self.memory_cmd) + 1)
            if self.index_cmd < len(self.memory_cmd):
                self.cmd.set(self.memory_cmd[self.index_cmd])

    fen = tk.Tk()

    viz = Vizualizer(fen)
    fen.grid_columnconfigure(0, weight=1)
    fen.grid_rowconfigure(0, weight=1)
    viz.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)

    fen.mainloop()
