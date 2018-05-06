#!/usr/bin/python

import sys
import os.path
import math
import random
from ctypes import *
from PIL import Image
from Crypto.Cipher import AES
from Crypto import Random

def read_and_encrypt(filename, key):
    array=[]
    f=open(filename, 'r')
    aes = AESCipher(key)
    enc = aes.encrypt(f.read())
    bytes = (ord(b) for b in enc)
    for b in bytes:
        for i in xrange(8):
            array.append((b >> i) & 1)
    return array


class AESCipher:
    def __init__( self, key ):
        self.key = key
        BS = 16
        self._pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
        self._unpad = lambda s : s[:-ord(s[len(s)-1:])]

    def encrypt( self, raw ):
        raw = self._pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return iv + cipher.encrypt( raw ) 

    def decrypt( self, enc ):
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        enc = self._pad(enc)
        return self._unpad(cipher.decrypt( enc[16:] ))



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
    msg_bits = read_and_encrypt(msg_file_path, "0123456789012345")
    print "msg len:", len(msg_bits)
    if len(msg_bits)>width*height*payload:
        print "Message too long"
        sys.exit(0)
    m = int(width*height*payload)
    message = (c_ubyte*m)()
    for i in range(m):
        if i<len(msg_bits):
            message[i] = msg_bits[i]
        else:
            message[i] = 0
    # Hide message
    stego = (c_int*(width*height))()
    a = lib.stc_hide(width*height, cover, costs, m, message, stego)
    print a, cover[4], stego[4]

    # Save output message
    idx=0
    for j in range(height):
        for i in range(width):
            im.putpixel((i, j), stego[idx])
            idx += 1
    im.save(output_img_path)
    im.close()
    


def extract(stego_img_path, output_msg_path, payload=0.40):

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
    m = int(n*payload)
    extracted_message = (c_ubyte*m)()
    s = lib.stc_unhide(n, stego, m, extracted_message)

    # Save the message
    enc = ''
    idx=0
    bitidx=0
    bitval=0
    for b in extracted_message:
        if bitidx==8:
            enc += chr(bitval)
            bitidx=0
            bitval=0
        bitval |= b<<bitidx
        bitidx+=1

    aes = AESCipher("0123456789012345")
    f = open(output_msg_path, 'w')
    f.write(aes.decrypt(enc))
    f.close()



