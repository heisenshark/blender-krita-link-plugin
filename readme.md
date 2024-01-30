# Blender Krita Link Plugin

This plugin offers a seamless way to edit Blender images in Krita without the need for file reloads.

## Features
- Links Blender textures with Krita files.
- Imports Blender textures as new layers.
- Selects UV faces in Blender (they must be selected in both edit mode and UV editor; this feature requires the C++ plugin).
- Transfers UV maps from selected objects in Blender to Krita.

![demo](demo.gif)

## Installation

The plugin consists of two parts: one for Blender and one for Krita.

### Blender Part
- Place the `BlenderKritaLink` folder in the `blender/version/scripts/addons/` directory.

### Krita Part
- Place `KritaBlenderLink` and `KritaBlenderDesktop.html` in the `<kritainstallation>/pykrita/` folder.

## Usage

### Enabling the Plugin
- In Krita: Activate the plugin via `Settings > Configure Krita > Python Plugin Manager`. Restart Krita and enable the dock under `Settings > Docker > Blender Krita Link`.
- In Blender: Enable the plugin through `Edit > Preferences > Add-ons > Blender Krita Link`.

### Krita Plugin Operation
- Use the `connect` button to link to Blender, or `disconnect` to end your session.
- The plugin loads images from Blender into a list. Link an image by right-clicking it and selecting `link image`, or import a texture by clicking `from blender to new layer`.
- To enable linking, ensure the Krita document is the same size as the Blender image. Set the correct color spectrum under `Image > Properties > Image Color Space` (RGB/Alpha and Profile: sRGB are recommended).
- If "Send on draw" is activated, the image will update in Blender when you release the draw button on the canvas (and use ctrl+(Shift)+Z). You can also send data manually using the "Send Data" button.
- Use `Refresh Images` to update image data from Blender.
- Use `Get UV Overlay` to get the UV map from selected object(in blender) to krita.
  - you can also change color of uv maps and their visibility

## UVselectAddition Installation
- The UV selection command requires compiling UVselectAddition.
- Compile Krita from source using [compile the krita](https://docs.krita.org/en/untranslatable_pages/building_krita.html) or [compile the krita using docker](https://docs.krita.org/en/untranslatable_pages/building/build_krita_with_docker_on_linux.html) if you encounter issues.
- Place `uv-select` from `cppPart` in the `krita>plugins` directory.
- Create an AppImage as per tutorials.
- Extract libraries and action files to your Krita installation as described in this [repository](https://github.com/Acly/krita-ai-tools).
- Note: Building on Windows hasn't been tested.

UVSelectionAddition is not required for the Python plugin to work but offers additional features.

### Disclaimer
This plugin is highly experimental and may contain bugs. If you wish to contribute or help improve it, feel free to contact me, make pull requests, or suggest improvements.