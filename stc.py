#!/usr/bin/python

import sys
import os.path
import math
import random
import struct
from ctypes import *
from PIL import Image
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random

def prepare_message(filename, key):

    f = open(filename, 'r')
    content_data = f.read()

    # Prepare a header with basic data about the message
    content_ver=struct.pack("B", 1) # version 1
    content_len=struct.pack("!I", len(content_data))
    content=content_ver+content_len+content_data

    # encrypt
    aes = AESCipher(key)
    enc = aes.encrypt(content)

    array=[]
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



def embed(input_img_path, msg_file_path, password, output_img_path, payload=0.40):

    me = os.path.abspath(os.path.dirname(__file__))
    lib = cdll.LoadLibrary(os.path.join(me, "lib", "stc.so"))

    # hash key
    hash = SHA256.new()
    hash.update(password)
    aes_key=hash.digest()

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
    msg_bits = prepare_message(msg_file_path, aes_key)
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
    


def extract(stego_img_path, password, output_msg_path, payload=0.40):

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

    # hash key
    hash = SHA256.new()
    hash.update(password)
    aes_key=hash.digest()

    # decrypt
    aes = AESCipher(aes_key)
    cleartext = aes.decrypt(enc)
 
    # Extract the header and the message
    content_ver=struct.unpack_from("B", cleartext, 0)
    content_len=struct.unpack_from("!I", cleartext, 1)
    content=cleartext[5:content_len[0]+5]

    f = open(output_msg_path, 'w')
    f.write(content)
    f.close()



