import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import math
import time
import os
import wda


c = wda.Client('http://localhost:8100')
s = wda.Client().session()

def pull_screenshot():
    #os.system('adb shell screencap -p /sdcard/1.png')
    #os.system('adb pull /sdcard/1.png .')
    c.screenshot('./1.png')

def jump(distance):
    press_time = distance * 2.07
    press_time = press_time * 0.001
    print press_time
    s.swipe(500, 1000, 500, 1001, press_time) # 0.5s

fig = plt.figure()
index = 0
cor = [0, 0]

pull_screenshot()
img = np.array(Image.open('1.png'))

update = True 
click_count = 0
cor = []

def update_data():
    return np.array(Image.open('1.png'))

im = plt.imshow(img, animated=True)


def updatefig(*args):
    global update
    if update:
        time.sleep(1.5)
        pull_screenshot()
        im.set_array(update_data())
        update = False
    return im,

def onClick(event):      
    global update    
    global ix, iy
    global click_count
    global cor

    # next screenshot
    
    ix, iy = event.xdata, event.ydata
    coords = []
    coords.append((ix, iy))
    print('now = ', coords)
    cor.append(coords)
    

    click_count += 1
    if click_count > 1:
        click_count = 0
        
        cor1 = cor.pop()
        cor2 = cor.pop()

        distance = (cor1[0][0] - cor2[0][0])**2 + (cor1[0][1] - cor2[0][1])**2 
        distance = distance ** 0.5
        print('distance = ', distance)
        jump(distance)
        update = True
        


fig.canvas.mpl_connect('button_press_event', onClick)
ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
plt.show()
