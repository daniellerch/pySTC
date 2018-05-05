#!/usr/bin/python

import sys
import os.path
import math
import random
from ctypes import *

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


