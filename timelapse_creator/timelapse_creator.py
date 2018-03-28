#!/usr/local/bin/python3 -v

from os import listdir
from os.path import isfile, join, basename
import argparse
import cv2

def imload(path):
    image = cv2.imread(path)
    return image
    #return cv2.resize(image,None,fx=0.5, fy=0.5, interpolation = cv2.INTER_LINEAR)

def main():
    parser = argparse.ArgumentParser(description='Turn sequences of PNGs into videos.')
    parser.add_argument('-output', '-o', type=str, help='Output file path.', required=True)
    parser.add_argument('-input', '-i', type=str, help='Input directory.', required=True)
    parser.add_argument('-harmonic', '-k', type=int, help='Skips all but every kth image in processing.')
    parser.add_argument('-skip', '-s', type=int, help='Skips first s images.')
    parser.set_defaults(harmonic=1, skip=0)
    args = parser.parse_args()

    output_path = args.output
    directory = args.input

    images = sorted([join(directory, f) for f in listdir(directory) if isfile(join(directory, f)) and ".png" in f])
    print("Image count: " + str(len(images)))

    img = imload(images[0])
    height, width, layers = shape = img.shape

    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"MJPG"), 30, (width, height))

    # write image (k*i + s) for all i=0,...,len(images)
    for i in range(args.skip, len(images)):
        if (i-args.skip) % args.harmonic != 0:
            continue
        img = imload(images[i])
        if img.shape != shape:
            print("Invalid shape: " + str(img.shape))
        writer.write(img)
        if i % 10 == 0:
            print("Progress: " + str(i*1.0 / len(images)))
    writer.release()

if __name__ == "__main__":
    main()
