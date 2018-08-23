#!/usr/local/bin/python3 -v

import cv2
import numpy as np
import os
import argparse
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description='Compress lossless sequences of AVIs to MP4.')
    parser.add_argument('-output', '-o', type=str, help='Output file path.', required=True)
    parser.add_argument('-input', '-i', type=str, help='Input file path.', required=True)
    args = parser.parse_args()
    convert(args.input, args.output)

def convert(ipath, opath):
    in_avi = cv2.VideoCapture(ipath)
    fourcc = cv2.VideoWriter_fourcc(*'x264')
    scale = 0.5
    w, h = int(scale*in_avi.get(cv2.CAP_PROP_FRAME_WIDTH)), int(scale*in_avi.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = in_avi.get(cv2.CAP_PROP_FPS)
    length = int(in_avi.get(cv2.CAP_PROP_FRAME_COUNT))
    print(fps)
    print(w, h)
    print(fourcc)

    out_mp4 = cv2.VideoWriter(opath, fourcc, fps, (w, h))

    for i in tqdm(range(length)):
        ret, frame = in_avi.read()
        frame = cv2.resize(frame,None,fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        out_mp4.write(frame)
    in_avi.release()
    out_mp4.release()

if __name__ == "__main__":
    main()
