#!/usr/bin/python

import stc

stc.embed('files/1.pgm', 'files/message.txt', 's3cr3t', 'files/stego.png')
stc.extract('files/stego.png', 's3cr3t', 'files/output.txt')

print open('files/output.txt', 'r').read()

