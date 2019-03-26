#!/usr/local/bin/python3 -v

from os import listdir
from os.path import isfile, join, basename
import argparse
import cv2

def imload(path):
    image = cv2.imread(path)
    return image
    #return cv2.resize(image,None,fx=0.5, fy=0.5, interpolation = cv2.INTER_LINEAR)

def addTime(img, text):
    cv2.putText(img,text, (25, 35), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(150,150,150))
    return img

def create_timelapse(directory, fps, output_path, offset, harmonic, renderProgress=None):
    images = sorted([join(directory, f) for f in listdir(directory) if isfile(join(directory, f)) and ".png" in f.lower()])
    print("Image count: " + str(len(images)))

    print(directory)
    if not len(images) > 0:
        print("No images found in directory! Make sure files are in PNG format.")
        return
    img = imload(images[0])
    height, width, layers = shape = img.shape

    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"MJPG"), fps, (width, height))

    # write image (k*i + s) for all i=0,...,len(images)
    for i in range(offset, len(images)):
        try:
            # get filename (without extension) from full path
            datestr = basename(images[i]).split(".")[0]
            date, time = datestr.split("_")
            time = ":".join(time.split("-"))
        except ValueError:
            date, time = "", ""

        if (i-offset) % harmonic != 0:
            continue
        img = imload(images[i])
        if img.shape != shape:
            print("Invalid shape: " + str(img.shape))
            continue

        img = addTime(img, date + "  " + time)

        writer.write(img)
        if i % 50 == 0:
            print("Progress: " + str(i*1.0 / len(images)))
        if renderProgress:
            renderProgress.emit(i*100.0 / len(images))
    writer.release()

def main():
    parser = argparse.ArgumentParser(description='Turn sequences of PNGs into videos.')
    parser.add_argument('-output', '-o', type=str, help='Output file path.', required=True)
    parser.add_argument('-input', '-i', type=str, help='Input directory.', required=True)
    parser.add_argument('-harmonic', '-k', type=int, help='Skips all but every kth image in processing.')
    parser.add_argument('-offset', '-s', type=int, help='Skips first s images.')
    parser.add_argument('--fps', '-fps', type=int, help='Framerate of output video.')
    parser.set_defaults(harmonic=1, skip=0)
    args = parser.parse_args()

    output_path = args.output
    directory = args.input
    offset = args.skip
    harmonic = args.harmonic

    create_timelapse(directory, fps, output_path, offset, harmonic)


if __name__ == "__main__":
    main()
