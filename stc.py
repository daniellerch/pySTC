#!/usr/bin/python

import sys
import os.path
import math
import random
from ctypes import *
from PIL import Image

def to_bits(filename):
    array=[]
    f=open(filename, 'r')
    bytes = (ord(b) for b in f.read())
    for b in bytes:
        for i in xrange(8):
            array.append((b >> i) & 1)
    return array

def embed(input_img_path, msg_file_path, output_img_path, payload=0.40):

    me = os.path.abspath(os.path.dirname(__file__))
    lib = cdll.LoadLibrary(os.path.join(me, "lib", "stc.so"))

    # Prepare cover image
    im=Image.open(input_img_path)
    if im.mode in ['L']:
        width, height = im.size
    if im.mode in ['RGB', 'RGBA', 'RGBX']:
        pass
    I = im.load()
    cover = (c_int*(width*height))()
    idx=0
    for j in range(height):
        for i in range(width):
            cover[idx] = I[i, j]
            idx += 1


    # Prepare costs
    INF = 2**31-1
    costs = (c_float*(width*height*3))()
    for i in range(width*height):
        if cover[i]==0:
            costs[3*i+0] = INF
            costs[3*i+1] = 0
            costs[3*i+2] = 1
        elif cover[i]==255:
            costs[3*i+0] = 1   
            costs[3*i+1] = 0 
            costs[3*i+2] = INF
        else:
            costs[3*i+0] = 1
            costs[3*i+1] = 0
            costs[3*i+2] = 1

    # Prepare message
    msg_bits = to_bits(msg_file_path)
    print "msg len:", len(msg_bits)
    if len(msg_bits)>width*height*payload:
        print "Message too long"
        sys.exit(0)
    message = (c_ubyte*len(msg_bits))()
    for i in range(len(msg_bits)):
        message[i] = msg_bits[i]
 
    # Hide message
    stego = (c_int*(width*height))()
    a = lib.stc_hide(width*height, cover, costs, len(msg_bits), message, stego)
    print a, cover[4], stego[4]

    # Save output message
    idx=0
    for j in range(height):
        for i in range(width):
            im.putpixel((i, j), stego[idx])
            idx += 1
    im.save(output_img_path)
    im.close()
    


def extract(stego_img_path, output_msg_path):

    me = os.path.abspath(os.path.dirname(__file__))
    lib = cdll.LoadLibrary(os.path.join(me, "lib", "stc.so"))

    # Prepare stego image
    im=Image.open(stego_img_path)
    if im.mode in ['L']:
        width, height = im.size
    if im.mode in ['RGB', 'RGBA', 'RGBX']:
        pass
    I = im.load()
    stego = (c_int*(width*height))()
    idx=0
    for j in range(height):
        for i in range(width):
            stego[idx] = I[i, j]
            idx += 1

    # Extract the message
    n = width*height;
    extracted_message = (c_ubyte*n)()
    s = lib.stc_unhide(n, stego, 5984, extracted_message)

    # Save the message
    f = open(output_msg_path, 'w')
    idx=0
    bitidx=0
    bitval=0
    for b in extracted_message:
        if bitidx==8:
            f.write(chr(bitval))
            bitidx=0
            bitval=0
        bitval |= b<<bitidx
        bitidx+=1
    f.close()




def _embed(input_img_path, msg_file_path, output_img_path, payload=0.40):

    me = os.path.abspath(os.path.dirname(__file__))
    lib = cdll.LoadLibrary(os.path.join(me, "lib", "stc.so"))


    random.seed(1)
    payload = 0.1

    INF = 2**31-1

    n = 512*512
    cover = (c_int*n)()
    costs = (c_float*(n*3))()
    for i in range(n):
        cover[i] = random.randint(0,255)
        if cover[i]==0:
            costs[3*i+0] = INF # INF
            costs[3*i+1] = 0
            costs[3*i+2] = 1
        elif cover[i]==255:
            costs[3*i+0] = 1   
            costs[3*i+1] = 0 
            costs[3*i+2] = INF # INF
        else:
            costs[3*i+0] = 1
            costs[3*i+1] = 0
            costs[3*i+2] = 1


    m = int(math.floor(payload*n)) 
    message = (c_ubyte*m)()


    str_message = "" 
    for i in range(m):
        b = random.randint(0,1)
        message[i] = b
        str_message += str(b)

    print "message:", str_message [:70]
    print "message:", str_message [-70:]


    stego = (c_int*n)()
    a = lib.stc_hide(n, cover, costs, m, message, stego)
    print a, cover[4], stego[4]

    extracted_message = (c_ubyte*m)()
    s = lib.stc_unhide(n, stego, m, extracted_message)

    str_message = "" 
    for i in range(m):
        str_message += str(extracted_message[i])
    print "message:", str_message [:70]
    print "message:", str_message [-70:]

    for i in range(m):
        if message[i] != extracted_message[i]:
            print "ERROR! different messages"
            break

