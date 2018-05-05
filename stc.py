#!/usr/bin/python

import sys
import os.path
import math
import random
from ctypes import *

me = os.path.abspath(os.path.dirname(__file__))
lib = cdll.LoadLibrary(os.path.join(me, "lib", "stc.so"))

INF = 10

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




lib.stc_hide(n, cover, costs)


