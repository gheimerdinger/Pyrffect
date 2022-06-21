import fusion_mode
import calc
import fusion_linear
from typing import Any, Tuple
import numpy as np
from PIL import Image
import sys
import subprocess as sp

FusionMode = fusion_linear.FusionMode
FusionLinear = fusion_linear.FusionLinear

FFMPEG = "ffmpeg"
class OutputImage:
    buffer: np.ndarray
    fusion_mode: FusionMode
    width: int
    height: int

    def __init__(
        self,
        width: int,
        height: int,
        framerate: int,
        out_file: str,
        fusion_mode: FusionMode = None,
    ) -> None:
        self.width = width
        self.height = height
        self.framerate = framerate
        self.out_file = out_file
        if fusion_mode is None:
            fusion_mode = FusionLinear()
        self.fusion_mode = fusion_mode
        self.buffer = np.full((self.height, self.width, 4), 0)

        self.save_command = [
                FFMPEG,
                '-y', 
                '-f', 'rawvideo',
                '-s', f'{self.width}x{self.height}',
                '-pix_fmt', 'rgb24',
                '-r', f'{self.framerate}',
                '-i', '-',
                '-an',
                '-crf', '10',
                '-vcodec', 'libx264',
                f'{self.out_file}'
            ]
        self.pipe = None
        self.logfile = open("log_file", "w+")

    def paste_on(self, calc: 'calc.Calc'):
        buffer = calc.out_buffer
        h, w, _ = buffer.shape
        w, h = min(w, calc.width), min(h, calc.height)
        x, y = calc.coords
        fx, fy = min(self.width, x + w), min(self.height, y + h)
        w = fx - x
        h = fy - y
        self.buffer[y:fy, x:fx] = self.fusion_mode.fuse(
            self.buffer[y:fy, x:fx], buffer[:h, :w]
        )

    def reset(self):
        self.buffer.fill(0)

    def printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        # Print New Line on Complete
        if iteration == total: 
            print()

    def save(self, iter, total):
        
        
        out = (self.buffer[:, :, :-1]).astype(np.uint8)
        if self.pipe is None:
            self.pipe = sp.Popen(self.save_command, stdin=sp.PIPE, stderr=self.logfile)
        self.printProgressBar(iter, total)
        try:
            self.pipe.stdin.write(out.tostring())
        except IOError as err:
            ffmpeg_error = None
            if ffmpeg_error is not None:
                ffmpeg_error = ffmpeg_error.decode()
            else:
                # The error was redirected to a logfile with `write_logfile=True`,
                # so read the error from that file instead
                self.logfile.seek(0)
                ffmpeg_error = self.logfile.read()

            error = (
                f"{err}\n\nMoviePy error: FFMPEG encountered the following error while "
                f"writing file {self.out_file}:\n\n {ffmpeg_error}"
            )

            if "Unknown encoder" in ffmpeg_error:
                error += (
                    "\n\nThe video export failed because FFMPEG didn't find the "
                    f"specified codec for video encoding mpeg. "
                    "Please install this codec or change the codec when calling "
                    "write_videofile.\nFor instance:\n"
                    "  >>> clip.write_videofile('myvid.webm', codec='libvpx')"
                )

            elif "incorrect codec parameters ?" in ffmpeg_error:
                error += (
                    "\n\nThe video export failed, possibly because the codec "
                    f"specified for the video {self.codec} is not compatible with "
                    f"the given extension {self.ext}.\n"
                    "Please specify a valid 'codec' argument in write_videofile.\n"
                    "This would be 'libx264' or 'mpeg4' for mp4, "
                    "'libtheora' for ogv, 'libvpx for webm.\n"
                    "Another possible reason is that the audio codec was not "
                    "compatible with the video codec. For instance, the video "
                    "extensions 'ogv' and 'webm' only allow 'libvorbis' (default) as a"
                    "video codec."
                )

            elif "bitrate not specified" in ffmpeg_error:

                error += (
                    "\n\nThe video export failed, possibly because the bitrate "
                    "specified was too high or too low for the video codec."
                )

            elif "Invalid encoder type" in ffmpeg_error:

                error += (
                    "\n\nThe video export failed because the codec "
                    "or file extension you provided is not suitable for video"
                )

            raise IOError(error)
        self.pipe.stdin.flush()

    def close(self):
        if self.pipe is not None:
            self.pipe.stdin.close()
            self.pipe.wait()
            self.pipe = None
