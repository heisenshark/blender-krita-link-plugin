# Blender Krita Link

This is a plugin for quick editting images in krita to use them as textures in blender, you can select krita document and set it to autoupdate one image in blender.
This plugin is highly experimental and you need to know how to use it

## Installation

Plugin is divided into blender and krita parts

Put blenderKritaLink folder in `blender/version/scripts/addons/` folder

Put KritaBlenderLink in `<kritainstallation>/pykrita/` folder

## Usage

to enable krita plugin enable it in krita preferences `Settings>Configure Krita>Python Plugin Manager` and restart krita, enable dock in `Settings>Docker>Blender Krita Link`

to enable blender plugin enable it in `Edit>Preferences>Add-ons>Blender Krita Link`

Blender Part is basically just a listener.

Krita plugin operates everything, click connect if blender or disconnect if you wanna finish your work.

At first you need to select an image to override, you need a document of same size to do it tho, also select correct color spectrum in `Image>Properties>Image Color Space` Model:RGB/Alpha **Depth: 32-bit float/channel** Profile:sRGB (others might work better if you also change color space in blender)

If Update on draw is set the image will update in blender if you release draw button on canvas, but you can also send data manually, using Send Data Button.

Refresh Images refreshes images data from blender

# Plugin is highly experimental and there **WILL** be bugs so be aware and if you wanna help this plugin grow contact me, make pull requests or smh
