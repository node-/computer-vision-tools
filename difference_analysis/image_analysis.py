#!/usr/local/bin/python3 -v

from os import listdir
from os.path import isfile, join, basename
from scipy import sum, average
from skimage import measure
from scipy.io import wavfile

import matplotlib.pyplot as plt
import numpy as np
import cv2
import argparse
import pickle

class Data(object):
    def __init__(self, n):
        self.t = np.asarray(range(n))
        self.freq = np.fft.fftfreq(self.t.shape[-1])
        self.ssim =  np.zeros(n)
        self.nrmse = np.zeros(n)
        self.manhattan = np.zeros(n)
        self.ssim_fft = np.array([])
        self.nrmse_fft = np.array([])
        self.manhattan_fft = np.array([])
        self.path = {}

    def to_tsv(self, pfile):
        with open(pfile+".tsv", 'a') as ptsv:
            ptsv.write("t\tssim\tnrmse\tmanhattan\timage\n")
            for t in self.t:
                row = [str(i) for i in [t, self.ssim[t], self.nrmse[t], self.manhattan[t], self.path[t]]]
                ptsv.write("\t".join(row) + "\n")

def main():
    parser = argparse.ArgumentParser(description='Analyze some images.')
    parser.add_argument('-pfile', '-p', type=str, help='analysis path', required=True)
    parser.add_argument('-directory', '-d', type=str, help='input path')
    parser.add_argument('-analyze', '-a', help='analyze file path', action='store_true')
    parser.set_defaults(analyze=False)
    args = parser.parse_args()

    if args.analyze:
        assert(args.directory)
        analyze(args.directory, args.pfile)
    view(args.pfile)

def view(pfile):

    data = pickle.load(open(pfile, "rb"))
    data.to_tsv(pfile)

    sound = data.manhattan/np.max(data.manhattan) - np.ones(data.manhattan.size)
    scaled = np.int16(sound/np.max(np.abs(sound)) * 32767)
    wavfile.write(pfile+".wav", 44100, scaled)


    plt.subplot(231)
    plt.ylabel("Structural Similarity")
    plt.xlabel("Time Step (t)")
    plt.plot(data.t, data.ssim, 'r')

    plt.subplot(232)
    plt.ylabel("Normalized RMS Deviation")
    plt.xlabel("Time Step (t)")
    plt.plot(data.t, data.nrmse, 'g')

    plt.subplot(233)
    plt.ylabel("Manhattan Difference")
    plt.xlabel("Time Step (t)")
    plt.plot(data.t, data.manhattan, 'b')

    plt.subplot(234)
    plt.ylabel("Amplitude")
    plt.xlabel("Frequency")
    plt.plot(data.freq, data.ssim_fft, 'r')

    plt.subplot(235)
    plt.xlabel("Frequency")
    plt.plot(data.freq, data.nrmse_fft, 'g')

    plt.subplot(236)
    plt.xlabel("Frequency")
    plt.plot(data.freq, data.manhattan_fft, 'b')

    plt.show()

def imload(path):
    image = cv2.imread(path)
    #return image
    return cv2.resize(image,None,fx=0.2, fy=0.2, interpolation = cv2.INTER_LINEAR)

def analyze(directory, pfile):
    images = sorted([join(directory, f) for f in listdir(directory) if isfile(join(directory, f)) and ".png" in f])
    n = len(images)
    data = Data(n)
    image_i = imload(images.pop(0))
    t = 0
    for path in images:
        image_f = imload(path)

        data.ssim[t] = measure.compare_ssim(image_f, image_i, multichannel=True)
        data.nrmse[t] = measure.compare_nrmse(image_f, image_i)
        data.manhattan[t] = sum(abs(image_f - image_i))
        data.path[t] = basename(path)

        image_i = image_f
        t += 1

    data.path[t] = ""
    data.ssim_fft = np.fft.fft(data.ssim)
    data.nrmse_fft = np.fft.fft(data.nrmse)
    data.manhattan_fft = np.fft.fft(data.manhattan)

    pickle.dump(data, open(pfile, 'wb'))

if __name__=="__main__":
    main()
