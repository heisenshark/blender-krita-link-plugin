import bpy
import numpy as np


class ImageManager():
    INSTANCE = None

    def __init__(self) -> None:
        if ImageManager.INSTANCE:
            return
        self.IMAGE: str = "Untitled"
        ImageManager.INSTANCE = self

    def mirror_image(self, image_pixels):
        print("hello from mirror_image")
        image = self.get_image()
        if not self.IMAGE or 'IMAGE UV_TEST'.find(image.type) == -1:
            print("object is not image. ", self.IMAGE, "  type:", image.type)
            return
        print("hello from mirror_image")
        width = image.size[0]
        height = image.size[1]
        print("hello from mirror_image")
        image_pixels.resize(len(image.pixels))

        pixels_reshaped = image_pixels.reshape((height, width, 4))
        mirrored_pixels = np.flipud(pixels_reshaped).flatten()
        print("hello from mirror_image")
        image.pixels.foreach_set(mirrored_pixels)

        print("hello from mirror_image")
        print(f"Image mirrored{image.name}")
        for obj in bpy.context.scene.objects:
            obj.update_tag()
        print("hello from mirror_image")

    def update_image(self, bytes_array):
        image = self.get_image()
        if not self.IMAGE or not image:
            return
        fp32_array = np.frombuffer(bytes_array, dtype=np.float32)
        fp32_array.resize(len(image.pixels))
        image.pixels.foreach_set(fp32_array)
        image.pack()
        for obj in bpy.context.scene.objects:
            obj.update_tag()

    def get_image(self):
        return bpy.data.images[self.IMAGE]

    def set_image_name(self, name):
        self.IMAGE = name

    def get_image_size(self):
        image = self.get_image()
        if self.IMAGE:
            return image.size
        else:
            return None
