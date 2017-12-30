# coding: utf-8
import os
import time
import math
import wda
from PIL import Image
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cbook as cbook
import cv2

mpl.rcParams['examples.directory']='./'

#get pic
def pull_screenshot():
    c.screenshot('./1.png')

#for debug
def backup_screenshot(ts):
    os.system('cp 1.png screenshot_backups/{}.png'.format(ts))

#do an action of jump
def jump(distance):
    press_time = distance * 2.23
    press_time = max(press_time, 0.2)
    print press_time*0.001
    s.swipe(500, 1000, 500, 1001, press_time*0.001) # 0.5s


def find_piece_and_board(im):
    w, h = im.size

    board_x = 0
    board_y = 0
    min_x = 999
    min_y = 0
    max_x = 0
    max_y = 0

    for i in range(h):
        for j in range(w):
            pixel = im.getpixel((j, i))
            # 根据棋子的最低行的颜色判断，找最后一行那些点的平均值
            if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                if j<min_x:
                    min_x = j
                    min_y = i
                if max_x < j:
                    max_x = j
                    max_y = i
   # print min_x,min_y
    #print max_x,max_y
    if not all((max_x, min_x, max_y, min_y)):
        return 0, 0, 0, 0
    #(x, y), position of you
    x = (min_x + max_x) / 2
    y = (min_y + max_y) / 2


#    image_file = cbook.get_sample_data('2.png')
#   image = plt.imread(image_file)
#      
#   plt.imshow(image)
#   plt.show()  
    img = np.array(Image.open('1.png'))
    plt.imshow(img, animated=True)
    plt.scatter(x,y, 25, color ='red')
#    plt.show()
    
    #Find boarder of net block
    cv_img = cv2.imread('1.png')
    gray_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    gradX = cv2.Sobel(gray_img, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradY = cv2.Sobel(gray_img, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)

    # subtract the y-gradient from the x-gradient
    gradient = cv2.subtract(gradX, gradY)
    gradient = cv2.convertScaleAbs(gradient)
    
    # blur and threshold the image
    blurred = cv2.blur(gradient, (9, 9))
    (_, thresh) = cv2.threshold(blurred, 90, 255, cv2.THRESH_BINARY)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    #closed = cv2.morphologyEx(gradient, cv2.MORPH_CLOSE, kernel)
    
    # perform a series of erosions and dilations
    closed = cv2.erode(closed, None, iterations=4)
    closed = cv2.dilate(closed, None, iterations=4)

    (_, cnts, _ ) = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c_1 = sorted(cnts, key=cv2.contourArea, reverse=True)[0]

    # compute the rotated bounding box of the largest contour
    rect = cv2.minAreaRect(c_1)
    box = np.int0(cv2.boxPoints(rect))

    # draw a bounding box arounded the detected barcode and display the image
    cv2.drawContours(cv_img, [box], -1, (0, 255, 0), 3)
    cv2.imshow("Image", cv_img)
    cv2.imwrite("contoursImage2.jpg", cv_img)
    #cv2.waitKey(0)

    cv2.imwrite('hh.png',closed)
    
    Xs = [i[0] for i in box]
    Ys = [i[1] for i in box]
    x1 = min(Xs)
    x2 = max(Xs)
    y1 = min(Ys)
    y2 = max(Ys)
    print x1, y1, x2, y2
    board_y = (y2 + y1)/2
    board_x = (x2 + x1)/2

  #  plt.imshow(img, animated=True)
 #   plt.scatter(board_x, board_y, 25, color ='red')
#    plt.show()

    if not all((board_x, board_y)):
        return 0, 0, 0, 0

    #return piece_x, piece_y, board_x, board_y
    return x, y, board_x, board_y


def main():
    while True:
        pull_screenshot()
        im = Image.open("./1.png")
        piece_x, piece_y, board_x, board_y = find_piece_and_board(im)
        ts = int(time.time())
        print(ts, piece_x, piece_y, board_x, board_y)
        distance = math.sqrt(abs(board_x - piece_x) ** 2 + abs(board_y - piece_y) ** 2)
        print distance
        jump(distance)
        backup_screenshot(ts)
        time.sleep(1.5)   # 为了保证截图的时候应落稳了，多延迟一会儿


if __name__ == '__main__':
    # Enable debug will see http Request and Response
    # wda.DEBUG = True
    c = wda.Client('http://localhost:8100')
    s = wda.Client().session()
    main()
