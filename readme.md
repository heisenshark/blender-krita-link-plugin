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

## UVselectAddition Installation

The UV selection command kinda works(in many cases but requires uvs of your selected object to not look like nightmare) but for it to work you need to install UVselectAddition somehow for a simple and maybe useful feature of creating krita selection area from uv map 

But you need to compile it first to do it
- you need to compile krita from source, thankfully there are guides [compile the krita](https://docs.krita.org/en/untranslatable_pages/building_krita.html) or if you are having problems(very probable) [compile the krita using docker](https://docs.krita.org/en/untranslatable_pages/building/build_krita_with_docker_on_linux.html)
- put the `uv-select` inside the  `krita>plugins` directory and 
- create appImage according to tutorials
- extract libraries(and action files) to your krita installation according to this [excellent repo](https://github.com/Acly/krita-ai-tools) and its releases

I haven't built it on windows yet so good luck with trying it on this platform.

Of course UvSelectionAddition is not required for python plugin to work

# Plugin is highly experimental and there **WILL** be bugs so be aware and if you wanna help this plugin grow contact me, make pull requests or smh
