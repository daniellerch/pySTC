#!/usr/bin/env python3

import os
import sys
import struct
import random
import numpy as np

from . import stc
from ctypes import *

INF = 2**31-1

def bytes_to_bits(data):
    array=[]
    for b in data:
        for i in range(8):
            array.append((b >> i) & 1)
    return array


def _hide_stc(cover_array, costs_array_m1, costs_array_p1, 
             message_bits, mx=255, mn=0):

    cover = (c_int*(len(cover_array)))()
    for i in range(len(cover_array)):
        cover[i] = int(cover_array[i])

    # Prepare costs
    costs = (c_float*(len(costs_array_m1)*3))()
    # 0: cost of changing by -1
    # 1: cost of not changing
    # 2: cost of changing by +1
    for i in range(len(costs_array_m1)):
        if cover[i]<=mn:
            costs[3*i+0] = INF
            costs[3*i+1] = 0
            costs[3*i+2] = costs_array_p1[i]
        elif cover[i]>=mx:
            costs[3*i+0] = costs_array_m1[i]
            costs[3*i+1] = 0 
            costs[3*i+2] = INF
        else:
            costs[3*i+0] = costs_array_m1[i]
            costs[3*i+1] = 0
            costs[3*i+2] = costs_array_p1[i]


    m = len(message_bits)
    message = (c_ubyte*m)()
    for i in range(m):
        message[i] = message_bits[i]

    # Hide message
    stego = (c_int*(len(cover_array)))()
    _ = stc.stc_hide(len(cover_array), cover, costs, m, message, stego)

    # stego data to numpy
    stego_array = cover_array.copy()
    for i in range(len(cover_array)):
        stego_array[i] = stego[i]
 
    return stego_array


def hide(message, cover_matrix, cost_matrix_m1, cost_matrix_p1,
         password_seed, mx=255, mn=0):
    random.seed(password_seed)

    message_bits = bytes_to_bits(message)

    height, width = cover_matrix.shape
    cover_array = cover_matrix.reshape((height*width,)) 
    costs_array_m1 = cost_matrix_m1.reshape((height*width,)) 
    costs_array_p1 = cost_matrix_p1.reshape((height*width,)) 

    # Hide data_len (32 bits) into 64 pixels (0.5 payload)
    data_len = struct.pack("!I", len(message_bits))
    data_len_bits = bytes_to_bits(data_len)

    # Shuffle
    indices = list(range(len(cover_array)))
    random.shuffle(indices)
    cover_array = cover_array[indices]
    costs_array_m1 = costs_array_m1[indices]
    costs_array_p1 = costs_array_p1[indices]

    stego_array_1 = _hide_stc(cover_array[:64], 
        costs_array_m1[:64], costs_array_p1[:64], data_len_bits, mx, mn)
    stego_array_2 = _hide_stc(cover_array[64:], 
        costs_array_m1[64:], costs_array_p1[64:], message_bits, mx, mn)
    stego_array = np.hstack((stego_array_1, stego_array_2))


    # Unshuffle
    stego_array[indices] = stego_array[list(range(len(cover_array)))]

    stego_matrix = stego_array.reshape((height, width))
  
    return stego_matrix


def _unhide_stc(stego_array, message_len):

    stego = (c_int*(len(stego_array)))()
    for i in range(len(stego_array)):
        stego[i] = int(stego_array[i])

    extracted_message = (c_ubyte*len(stego_array))()
    s = stc.stc_unhide(len(stego_array), stego, message_len, extracted_message)

    if len(extracted_message) < message_len:
        print("WARNING, inconsistent message lenght:", 
              len(extracted_message), ">", message_len)
        return bytearray()

    # Message bits to bytes
    data = bytearray()
    idx=0
    bitidx=0
    bitval=0
    for i in range(message_len):
        if bitidx==8:
            data.append(bitval)
            bitidx=0
            bitval=0
        bitval |= extracted_message[i]<<bitidx
        bitidx+=1
        idx += 1
    if bitidx==8:
        data.append(bitval)

    data = bytes(data)
    return data


def unhide(stego_matrix, password_seed):

    random.seed(password_seed)

    height, width = stego_matrix.shape
    stego_array = stego_matrix.reshape((height*width,))

    # Shuffle
    indices = list(range(len(stego_array)))
    random.shuffle(indices)
    stego_array = stego_array[indices]

    # Extract a 32-bits message lenght from a 64-pixel array
    data = _unhide_stc(stego_array[:64], 32)
    data_len = struct.unpack_from("!I", data, 0)[0]
    
    data = _unhide_stc(stego_array[64:], data_len)
    return data






