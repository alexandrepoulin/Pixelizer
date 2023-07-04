# Pixelizer
A python script that can convert an image into a pixelized version


There are a few parameters at the start of the script that you can change to change how the image is pixelized.

The way this works is by using a clustering algorithm to find some number of centroid colors for the image. It then generates different shade of those colors. Finally, it goes through the image, averages the colors over a chosen pixel size, finds the closest color in the pallet, and set the value to that color. If you have the same_size option on, it will replace all the pixels with the chosen color.

Some things you can modify:
* The number of colors found in the clustering algorithm
* The number of shades brighter to add to the pallet
* The number of shades darker to add to the pallet
* How the different shades are generated. These are changed in the HSV color space.
    * For brighter shades, the saturation is divided by a factor and the value is multiplied by a value
    * For darker shades, the saturation is multiplied by a factor and the value is divided by a value. The hue is also blue shifted closer to a value of 2/3 by some fixed amount. This takes into account that values below 1/6th will decrease in value.
* You can also change the saturation of and value of the cluster colors by a multiplicative factor to either make them more dull and calm, or brighter and eye watering.
* Finally, to make sure things map in the correct way, you can modify the color before a pallet color is chosen. This is to have wonky effects.


