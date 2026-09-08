from multiprocessing import Lock
import bpy
import numpy as np
import time
from .logger import logger


class ImageManager:
    INSTANCE = None
    UPDATING_IMAGE = Lock()

    def __init__(self) -> None:
        if not ImageManager.INSTANCE:
            self.IMAGE_NAME = None
            ImageManager.INSTANCE = self

    def update_image(self, image_pixels, image_name):
        logger.debug("mirror_image started")
        t = time.time()
        image = self.get_image(image_name)
        if not image or "IMAGE UV_TEST".find(image.type) == -1:
            logger.warning("object is not image. %s type: %s", self.IMAGE_NAME, image.type if image else "None")
            return

        logger.debug("mirror_image loaded in %s", time.time() - t)
        width = image.size[0]
        height = image.size[1]
        logger.info(
            "mirror_image sizes: image=%s, input=%s, dim=%sx%s",
            len(image.pixels),
            len(image_pixels),
            width,
            height,
        )
        logger.debug(
            "bef reshaped details: input=%s, len=%s, w_ratio=%s, h_ratio=%s",
            image_pixels,
            len(image_pixels),
            len(image_pixels) / width / 4,
            len(image_pixels) / height / 4,
        )
        image_pixels = image_pixels.reshape(-1, 4)
        logger.debug("reshaped complete")
        if isinstance(image_pixels[0][0], np.uint16) or isinstance(
            image_pixels[0][0], np.uint8
        ):
            image_pixels[:, [2, 0]] = image_pixels[:, [0, 2]]
        logger.debug("flipped complete")

        image_pixels.resize(len(image.pixels))
        logger.debug("resized complete")
        pixels_reshaped = image_pixels.reshape((height, width, 4))
        logger.debug("reshaped2 complete")
        mirrored_pixels = np.flipud(pixels_reshaped).flatten()
        logger.info(
            "mirror_image processed: mirrored=%s, reshaped=%s, time=%s",
            len(mirrored_pixels),
            len(pixels_reshaped),
            time.time() - t,
        )
        logger.debug("pixel type details: %s %s type=%s", mirrored_pixels[0], mirrored_pixels[1], type(mirrored_pixels[0]))

        if isinstance(mirrored_pixels[0], np.uint16):
            mirrored_pixels = np.divide(
                mirrored_pixels, np.array(np.float32(255 * 255))
            )

        if isinstance(mirrored_pixels[0], np.uint8):
            mirrored_pixels = np.divide(mirrored_pixels, np.array(np.float32(255)))
        logger.debug("pixel division details: %s %s", mirrored_pixels[0], mirrored_pixels[1])

        image.pixels.foreach_set(mirrored_pixels.astype(np.float32))
        image.update()
        image.update_tag()
        logger.info("mirror_image completed in %s", time.time() - t)

        if image.is_float:  # I dont know what it is anymore and even how to test this
            image.pack()
            image.alpha_mode = "PREMUL"
            image.alpha_mode = "STRAIGHT"
        logger.info("mirror_image packed and alpha updated in %s", time.time() - t)

    def get_image(self, name=None):
        if name is not None:
            return bpy.data.images[name]
        if not self.IMAGE_NAME:
            return None
        return bpy.data.images[self.IMAGE_NAME]

    def get_image_from_name(self, name):
        return bpy.data.images[name]

    def set_image_name(self, name: str | None):
        self.IMAGE_NAME = name

    def get_image_size(self, name=None):
        image = self.get_image(name)
        if image:
            return image.size
        else:
            return None
