#!/usr/bin/env python3

import pystc
import numpy as np
import imageio.v3 as iio
import warnings
from scipy import signal

warnings.filterwarnings('ignore', category=RuntimeWarning)

input_image = 'image.pgm'

def HILL(I):
    H = np.array(
       [[-1,  2, -1],
        [ 2, -4,  2],
        [-1,  2, -1]])
    L1 = np.ones((3, 3)).astype('float32')/(3**2)
    L2 = np.ones((15, 15)).astype('float32')/(15**2)
    costs = signal.convolve2d(I, H, mode='same')  
    costs = abs(costs)
    costs = signal.convolve2d(costs, L1, mode='same')  
    costs = 1/costs
    costs = signal.convolve2d(costs, L2, mode='same')  
    costs[costs == np.inf] = 1
    return costs

I = iio.imread(input_image)

costs = HILL(I)
seed = 32 # secret seed

message = "Hello World".encode()
stego = pystc.hide(message, I, costs, costs, seed, mx=255, mn=0)

message_extracted = pystc.unhide(stego, seed)
print("Extracted:", message_extracted.decode())







