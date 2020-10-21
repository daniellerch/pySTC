#!/usr/bin/env python3

import stc
import numpy as np
import imageio
from scipy import signal

input_image = 'files/1.pgm'

def HILL(input_image):
    H = np.array(
       [[-1,  2, -1],
        [ 2, -4,  2],
        [-1,  2, -1]])
    L1 = np.ones((3, 3)).astype('float32')/(3**2)
    L2 = np.ones((15, 15)).astype('float32')/(15**2)
    I = imageio.imread(input_image)
    costs = signal.convolve2d(I, H, mode='same')  
    costs = abs(costs)
    costs = signal.convolve2d(costs, L1, mode='same')  
    costs = 1/costs
    costs = signal.convolve2d(costs, L2, mode='same')  
    costs[costs == np.inf] = 1
    return costs

costs = HILL(input_image)
print(costs)

stc.embed(input_image, costs, 'files/message.txt', 's3cr3t', 'files/stego.png')
stc.extract('files/stego.png', 's3cr3t', 'files/output.txt')

print(open('files/output.txt', 'r').read())




