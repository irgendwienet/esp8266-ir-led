from machine import Pin, freq
from neopixel import NeoPixel
from sys import platform

import time 
import ir_rx
import math
import gc

from ir_rx.nec import NEC_8

freq(160000000)

# The pin connected to TSOP4838 as an input
tsopPin = Pin(13, Pin.IN) # pin 13 is also called D7

# the pin controlling the WS2812 LEDs as output
numberOfLeds = 4
ledPin = Pin(4, Pin.OUT)  # pin 4 is also called D2
leds = NeoPixel(ledPin, numberOfLeds) 

print ('init done')

### LED Helper ###
def setAllTo(rgb):
    for i in range(numberOfLeds):
      leds[i] = (rgb)
    leds.write()    

# turns all LEDs off
def clear(): 
    setAllTo (toRgb(0,0,0))
    
# HSV color values to RGB used by the LEDs. See https://en.wikipedia.org/wiki/HSL_and_HSV
def toRgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

currentH = 0.0
currentS = 0.0
currentV = 0.3

def showCurrent():
    print(f"{currentH} {currentS} {currentV}")
    setAllTo(toRgb(currentH, currentS, currentV))

# this callback function is called every time the ir library received something
def irCmdReceivedCallback(data, addr, ctrl):
    global currentH
    global currentS
    global currentV

    if data < 0:  # NEC protocol sends repeat codes.
        print("Repeat code.")
    else:
        print(f"Data 0x{data:02x} Addr 0x{addr:04x} Ctrl 0x{ctrl:02x}")

        if data == 0x19: # red
            currentH = 0
            currentS = 1
        elif data == 0x1b: # green
            currentH = 120
            currentS = 1
        elif data == 0x11: # blue
            currentH = 250
            currentS = 1
        elif data == 0x15: # white
            currentS = 0

        elif data == 0x17: # dark orange
            currentH = 25
            currentS = 1
        elif data == 0x12: # lighter green
            currentH = 130
            currentS = 1
        elif data == 0x16: # lighter blue
            currentH = 195
            currentS = 1
        elif data == 0x4d: # black blue
            currentH = 270
            currentS = 1

        elif data == 0x40: # light orange
            currentH = 40
            currentS = 1
        elif data == 0x4c: # light green
            currentH = 140
            currentS = 1
        elif data == 0x04: # light blue
            currentH = 170
            currentS = 1
        elif data == 0x00: # purple
            currentH = 280
            currentS = 1

        elif data == 0x0a: # yellow
            currentH = 60
            currentS = 1
        elif data == 0x1e: # dark green
            currentH = 100
            currentS = 0.5
        elif data == 0x0e: # darker purple
            currentH = 170
            currentS = 1
        elif data == 0x1a: # lighter purple
            currentH = 270
            currentS = 1  

        elif data == 0x0c and currentV >= 0.1: # speed- used for brightness-
            currentV -= 0.1
        elif data == 0x0f and currentV <= 0.9: # speed+ used for brightness+
            currentV += 0.1


        elif data == 0x10: # on
            showCurrent()
            return
        elif data == 0x03: # off
            clear()
            return
        
        showCurrent()

        
# turn on the receiver and hook it up with the callback function
ir = NEC_8(tsopPin, irCmdReceivedCallback) 

try:
    while True:
        print("running")
        time.sleep(5)
        gc.collect()
except KeyboardInterrupt:
    ir.close()
