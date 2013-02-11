Maya Fluid Texture Manipulators version 1.0
============================

create 3 controllers for the fluid texture parameters in Maya (origin, rotate, scale, implode)

All the rig exists under a group named *fluidTextureManipulators#* in the world.
So deleting this group will delete the entire rig.

*FT_RotateAndScaleCtrl#*:

* **rotate** change the texture rotate of the fluid.

* **scale** change the texture scale of the fluid.

* **control size** change just the scale of the controls (purely cosmetic)

* **ruler display** display some rulers on every axis to help visualize the scale. The rulers can be rotated on it's own so you match a feature of your fluid.

* **ruler divisions** how many divisions you can see on the rulers

* **ruler width mult** increase the width of the rulers

*FT_OriginCtrl#*:

* **translate** change the texture origin of the fluid.

* **scale** change the size of the control (purely cosmetic)

* **visibility** visibility of the control

* **frequency dependent space** the texture origin of a fluid is actually dependent on the frequency. But this will free the controller from the frequency, so you can animate it and later change the frequency and still have a correct 3D space translation of the texture

this controller's parent is a group that allow you to offset the controller position in the world to match a feature of your fluid (without affecting the fluid texture origin values) and start a tracking for example.

*FT_ImplodeCtrl#*:

* **translate** change the texture's implode position of the fluid.

* **scale** change the size of the control (purely cosmetic)

* **visibility** visibility of the control

## Why?

On some occasions, like a very directional smoke for example, it can be nice to animate the fluid texture translation to follow the fluid movement. But Maya fluid texture transformations are difficult to visualize and control. It's also poorly documented, like the implode center. I notice that many people think that the implode position is in world space while it's actually not exactly world space, also implode is dependent on the textureRotate but not on the textureScale. So this rig give a good and precise way to animate those parameters and match the texture transformations with the movement of some features of your fluid.

## Usage in Maya

2 ways:
* select a fluid, then copy/paste this into a Maya python script editor and
execute it.
* put the script into a python script folder which path is known by Maya, then use an import
command to use the script and call the main function with appropriate parameters.

This script use pymel, so if you can't import pymel you are in trouble.

## Main function to call?

FTM_addFluidTextureManipulators( fluid )

## Contact
feedback? bugs? request?... feel free to contact me
mathieu@hiddenforest.fr
