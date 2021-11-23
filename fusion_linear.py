from PIL import Image
import fusion_mode

FusionMode = fusion_mode.FusionMode


class FusionLinear:
    @staticmethod
    def fuse(imageA, imageB):
        imageA = imageA * (1 - imageB[:, :, 3, None]) + imageB * imageB[:, :, 3, None]
        imageA[:, :, 3] = 1.0
        return imageA
