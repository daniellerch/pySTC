#!/usr/bin/python

import sys
import stc

stc.embed('files/1.pgm', 'files/message.txt', 'files/stego.png')
stc.extract('files/stego.png', 'files/output.txt')

print open('files/output.txt', 'r').read()

