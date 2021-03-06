#!/usr/local/bin/python3 -v

from os import listdir
from os.path import isfile, join, basename
import argparse
import cv2

from datetime import datetime
from time import sleep
import pandas as pd
import numpy as np
from tqdm import tqdm

def alert():
    print(' '.join(['\a']*3)); sleep(1); print(' '.join(['\a']*3))
    input("Press Enter to continue...")


class Temps(object):
    def __init__(self, infile):
        self.df = pd.read_pickle(infile)

        print(self.df.shape)
        self.df = self.df.loc[~self.df.index.duplicated(keep='first')]
        print(self.df.shape)

    def on(self, date, temp_column):
        d = datetime.strptime(date, "%Y-%m-%d_%H-%M-%S")
        #true_index = self.df["timestamp"].index.get_loc(d, method='nearest')
        #select_indices = list(np.where(abs(df["timestamp"] - d))[0])
        true_index = int((self.df["date"]-d).abs().argsort()[:1])

        #print(self.df.iloc[true_index])
        #print(datetime.strptime(date, "%Y-%m-%d_%H-%M-%S"))
        return self.df.iloc[true_index][temp_column]

    def addTemps(self, img, datestr, cols, startx, starty):
        dy = 70
        i = 0
        for col in cols:
            text = cols[col] + ": "
            temp = format(self.on(datestr, temp_column=col), '.1f') + " K"
            # align numbers by splitting TC names and values
            img = addTemp(img, text, startx, starty+dy*i)
            img = addTemp(img, temp, startx+500, starty+dy*i)
            i += 1
        return img

def imload(path):
    image = cv2.imread(path)
    #return image
    return cv2.resize(image,None,fx=0.50, fy=0.50, interpolation = cv2.INTER_LINEAR)

def addTemp(img, text, x, y):
    cv2.putText(img,text, (x,y), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1.7, color=(255,255,255), thickness=1)
    return img



def addTime(img, text):
    cv2.putText(img,text, (25, 35), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1.5, color=(150,150,150))
    return img

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

    temps = Temps(r"C:\Users\kosberg\code\data-tools\data_image.pkl")

    # write image (k*j + s) for all j = i-s = 0,...,len(images)-s
    for i in tqdm(range(args.skip, len(images))):
        datestr = images[i].split("\\")[-1].split(".")[0]
        date, time = datestr.split("_")
        time = ":".join(time.split("-"))

        if (i-args.skip) % args.harmonic != 0:
            continue
        
        try:
            img = imload(images[i])
            #aise cv2.error("test error")
        except cv2.error as e:
            print(e)
            alert()

        if img.shape != shape:
            print("Invalid shape: " + str(img.shape))
            continue

        img = addTime(img, date + "  " + time)
        img = temps.addTemps(img, datestr, cols={"TC_20":"Peak", "TC_18":"Under Peak", "TC_15":"Trough"}, startx=int(width/9), starty=int(height/5))

        writer.write(img)
    writer.release()

if __name__ == "__main__":
    main()
