from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from cv2 import cv2
from PIL import Image
import matplotlib.pyplot as plt
import os

counter = 0
prev_point = []

def click_data(event, x, y, flags, param):
  global counter, prev_point
  if (event == cv2.EVENT_LBUTTONDOWN):
    print('\nSelected point: ',x,',',y)
    if counter >= 1:   
        print('> Difference from previous point: ',x-prev_point[0],',',y-prev_point[1])
    prev_point = [x,y]
    colorsBGR = image[y, x]
    colorsRGB = tuple(reversed(colorsBGR)) #Reversing the OpenCV BGR format to RGB format
    print("> RGB Value: {}".format(colorsRGB))
    counter = counter + 1

def conversion(path):
    size = len(path)
    im = Image.open(path)
    rgb_im = im.convert('RGB')
    rgb_im.save(path[:size-4]+'.jpg')


if __name__ == "__main__":
    root = Tk()
    root.wm_attributes('-alpha', 0)
    filename = fd.askopenfilename()
    path = filename
    size = len(path)

    conversion(path)
    image = cv2.imread(path[:size-4]+'.jpg')

    cv2.namedWindow('Image', cv2.WINDOW_GUI_EXPANDED)
    cv2.resizeWindow('Image', 1200, 900)
    cv2.imshow('Image', image)
    cv2.setMouseCallback('Image', click_data)

    while (1):
        cv2.namedWindow('Image', cv2.WINDOW_GUI_EXPANDED)
        cv2.resizeWindow('Image', 1200, 900)
        cv2.imshow('Image', image)
        if cv2.waitKey(10) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
        
    if(path.endswith('.CR2')):
        os.remove(path[:size-4]+'.jpg')
