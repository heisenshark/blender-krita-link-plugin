from multiprocessing import Lock
import bpy
import numpy as np
import time


class ImageManager:
    INSTANCE = None
    UPDATING_IMAGE = Lock()

    def __init__(self) -> None:
        if not ImageManager.INSTANCE:
            self.IMAGE_NAME = None
            ImageManager.INSTANCE = self

    def update_image(self, image_pixels,image_name):
        print("hello from mirror_image")
        t = time.time()
        image = self.get_image(image_name)
        if not image or "IMAGE UV_TEST".find(image.type) == -1:
            print("object is not image. ", self.IMAGE_NAME, "  type:", image.type)
            return

        print("hello from mirror_image", time.time() - t)
        width = image.size[0]
        height = image.size[1]
        print(
            "hello from mirror_image",
            len(image.pixels),
            len(image_pixels),
            width,
            height,
        )
        print("bef reshaped", image_pixels, len(image_pixels),len(image_pixels)/width/4,len(image_pixels)/height/4)
        image_pixels = image_pixels.reshape(-1, 4)
        print("reshaped")
        if isinstance(image_pixels[0][0], np.uint16) or isinstance(
            image_pixels[0][0], np.uint8
        ):
            image_pixels[:, [2, 0]] = image_pixels[:, [0, 2]]
        print("flipped")

        image_pixels.resize(len(image.pixels))
        print("resized")
        pixels_reshaped = image_pixels.reshape((height, width, 4))
        print("reshaped2")
        mirrored_pixels = np.flipud(pixels_reshaped).flatten()
        print(
            "hello from mirror_image",
            len(mirrored_pixels),
            len(pixels_reshaped),
            time.time() - t,
        )
        print(mirrored_pixels[0], mirrored_pixels[1], type(mirrored_pixels[0]))

        if isinstance(mirrored_pixels[0], np.uint16):
            mirrored_pixels = np.divide(
                mirrored_pixels, np.array(np.float32(255 * 255))
            )

        if isinstance(mirrored_pixels[0], np.uint8):
            mirrored_pixels = np.divide(mirrored_pixels, np.array(np.float32(255)))
        print(mirrored_pixels[0], mirrored_pixels[1])
        
        image.pixels.foreach_set(mirrored_pixels.astype(np.float32))
        image.update()
        image.update_tag()
        print("hello from mirror_image", time.time() - t)

        if image.is_float:  # I dont know what it is anymore and even how to test this 
            image.pack()
            image.alpha_mode = "PREMUL"
            image.alpha_mode = "STRAIGHT"
        print("hello from mirror_image, packed, alfa changed ", time.time() - t)

    def get_image(self,name = None):
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
