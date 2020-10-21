#!/usr/bin/env python3

import sys
import os.path
import math
import random
import struct
import hashlib
from PIL import Image
from ctypes import *
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

def prepare_message(filename, password):

    f = open(filename, 'r')
    content_data = f.read().encode('utf-8')

    # Prepare a header with basic data about the message
    content_ver=struct.pack("B", 1) # version 1
    content_len=struct.pack("!I", len(content_data))
    content=content_ver+content_len+content_data

    # encrypt
    enc = encrypt(content, password)

    array=[]
    for b in enc:
        for i in range(8):
            array.append((b >> i) & 1)
    return array


# {{{ encrypt()
def encrypt(plain_text, password):

    salt = get_random_bytes(AES.block_size)

    # use the Scrypt KDF to get a private key from the password
    private_key = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

    cipher = AES.new(private_key, AES.MODE_CBC)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    enc = salt+cipher.iv+cipher_text

    return enc
# }}}

# {{{ decrypt()
def decrypt(cipher_text, password):
    
    salt = cipher_text[:AES.block_size]
    iv = cipher_text[AES.block_size:AES.block_size*2]
    cipher_text = cipher_text[AES.block_size*2:]

    # Fix padding
    mxlen = len(cipher_text)-(len(cipher_text)%AES.block_size)
    cipher_text = cipher_text[:mxlen]

    private_key = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

    cipher = AES.new(private_key, AES.MODE_CBC, iv=iv)
    decrypted = cipher.decrypt(cipher_text)
    #decrypted = unpad(decrypted, AES.block_size)

    return decrypted
# }}}




def embed(input_img_path, cost_matrix,  msg_file_path, password, output_img_path, payload=0.40):

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
    idx=0
    for j in range(height):
        for i in range(width):
            if cover[idx]==0:
                costs[3*idx+0] = INF
                costs[3*idx+1] = 0
                costs[3*idx+2] = cost_matrix[i, j]
            elif cover[idx]==255:
                costs[3*idx+0] = cost_matrix[i, j]
                costs[3*idx+1] = 0 
                costs[3*idx+2] = INF
            else:
                costs[3*idx+0] = cost_matrix[i, j]
                costs[3*idx+1] = 0
                costs[3*idx+2] = cost_matrix[i, j]
            idx += 1

    # Prepare message
    msg_bits = prepare_message(msg_file_path, password)
    if len(msg_bits)>width*height*payload:
        print("Message too long")
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
    enc = bytearray()
    idx=0
    bitidx=0
    bitval=0
    for b in extracted_message:
        if bitidx==8:
            enc.append(bitval)
            bitidx=0
            bitval=0
        bitval |= b<<bitidx
        bitidx+=1
    if bitidx==8:
        enc.append(bitval)

    # decrypt
    cleartext = decrypt(enc, password)
 
    # Extract the header and the message
    content_ver=struct.unpack_from("B", cleartext, 0)
    content_len=struct.unpack_from("!I", cleartext, 1)
    content=cleartext[5:content_len[0]+5]

    f = open(output_msg_path, 'w')
    f.write(content.decode())
    f.close()



