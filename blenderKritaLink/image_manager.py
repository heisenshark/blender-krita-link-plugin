import bpy
import numpy as np

class ImageManager:
    INSTANCE = None

    def __init__(self) -> None:
        if not ImageManager.INSTANCE:
            self.IMAGE_NAME = None
            ImageManager.INSTANCE = self
    
    def mirror_image(self, image_pixels):
        print("hello from mirror_image")
        image = self.get_image()
        if not image or "IMAGE UV_TEST".find(image.type) == -1:
            print("object is not image. ", self.IMAGE_NAME, "  type:", image.type)
            return
        print("hello from mirror_image")
        width = image.size[0]
        height = image.size[1]
        print(
            "hello from mirror_image",
            len(image.pixels),
            len(image_pixels),
            width,
            height,
        )

        image_pixels = image_pixels.reshape(width * height,4)

        if isinstance(image_pixels[0][0], np.uint16) or isinstance(
            image_pixels[0][0], np.uint8
        ):
            image_pixels[:, [2, 0]] = image_pixels[:, [0, 2]]

        image_pixels.resize(len(image.pixels))
        pixels_reshaped = image_pixels.reshape((height, width, 4))

        mirrored_pixels = np.flipud(pixels_reshaped).flatten()
        print("hello from mirror_image", len(mirrored_pixels), len(pixels_reshaped))
        print(mirrored_pixels[0], mirrored_pixels[1], type(mirrored_pixels[0]))

        if isinstance(mirrored_pixels[0], np.uint16):
            mirrored_pixels = np.divide(
                mirrored_pixels, np.array(np.float32(255 * 255))
            )

        if isinstance(mirrored_pixels[0], np.uint8):
            mirrored_pixels = np.divide(mirrored_pixels, np.array(np.float32(255)))
        print(mirrored_pixels[0], mirrored_pixels[1])

        image.pixels.foreach_set(mirrored_pixels.astype(np.float32))

        print("hello from mirror_image")
        print(f"Image mirrored{image.name}")
        for obj in bpy.context.scene.objects:
            obj.update_tag()
        print("hello from mirror_image")

        if image.is_float:
            image.pack()
            image.alpha_mode = "PREMUL"
            image.alpha_mode = "STRAIGHT"

    def update_image(self, bytes_array):
        image = self.get_image()
        if not image:
            return
        fp32_array = np.frombuffer(bytes_array, dtype=np.float32)
        fp32_array.resize(len(image.pixels))
        image.pixels.foreach_set(fp32_array)
        image.pack()
        for obj in bpy.context.scene.objects:
            obj.update_tag()

    def get_image(self):
        if not self.IMAGE_NAME:
            return None
        return bpy.data.images[self.IMAGE_NAME]

    def set_image_name(self, name: str | None):
        self.IMAGE_NAME = name

    def get_image_size(self):
        image = self.get_image()
        if image:
            return image.size
        else:
            return None
