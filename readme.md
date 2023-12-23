# Blender Krita Link

This plugin provides quick way to edit blender images in krita with no need for file reloads.

## Installation

Plugin is divided into blender and krita parts

### Blender Part

Put `blenderKritaLink` folder in `blender/version/scripts/addons/` folder

### Krita Part

Put `KritaBlenderLink` and `KritaBlenderDesktop.html` in `<kritainstallation>/pykrita/` folder

## Usage

to enable plugin in krita enable it in krita preferences `Settings>Configure Krita>Python Plugin Manager` and restart krita, after that enable dock in `Settings>Docker>Blender Krita Link`

to enable blender plugin enable it in `Edit>Preferences>Add-ons>Blender Krita Link`

Krita plugin operates everything, click connect if blender or disconnect if you wanna finish your work.

At first you need to select an image to override, document should be of same size as blender image, also select correct color spectrum in `Image>Properties>Image Color Space` Model:RGB/Alpha **Depth: 32-bit float/channel** Profile:sRGB (others might also work if you also change color space in blender)

If Update on draw is set the image will update in blender if you release draw button on canvas, but you can also send data manually, using Send Data Button.

Refresh Images refreshes images data from blender

# Plugin is highly experimental and there **WILL** be bugs so be aware and if you wanna help this plugin grow contact me, make pull requests or smh
