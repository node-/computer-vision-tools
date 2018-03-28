# computer-vision-tools
A collection of discrete python scripts for image-related tasks.

# timelapse_creator.py

Requires: Python3, OpenCV3

This script creates a timelapse video (.avi) out of alphanumerically sorted images (.png) from an input directory.
It can also skip any number of initial images, and it can skip all but every kth image for any k (perhaps λ would be better).

This example creates a timelapse from all images in ```input_directory```.
```python3 timelapse_creator.py -i input_directory -o output.avi```

This example creates a timelapse from every 14 images starting from the 10th image.
```python3 timelapse_creator.py -i input_directory -o harmonic_output.avi -k 14 -s 10```

# image_analysis.py

Requires: Python3, OpenCV3, scikit-image, matplotlib

This script analyzes a sequence of images (sorted alphanumerically) by plotting the difference between temporally adjacent images.

There are three difference functions which are outputted: Manhattan norm, Structural Similarity, and Normalized RMS.

It ouputs a tab-delimited text file of the data (.tsv), a serialization of the data (to be loaded into matplotlib through the script), and a wav file of the normalized Manhattan distance (just for fun).

Here is a rule of thumb for the difference functions:
```
ssim - metric based on human perceptual differences (structure, light, contrast)
nrmse - standard general metric, represents residual of data
manhattan - sum of absolute values, represents change in data
```

This example analyzes an input directory and outputs it to ```pickle.p```.
```python3 image_analysis.py -d input_directory -p pickle.p -a

This example does NOT analyze any images, and simply displays an existing pickled analysis (i.e., pickle.p is the input).
```python3 image_analysis.py -p pickle.p```
