from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from cv2 import cv2
from PIL import Image
import matplotlib.pyplot as plt
import os

# global variables
counter = 0
prev_point = []

# click mouse actions
def click_data(event, x, y, flags, param):
  global counter, prev_point
  if (event == cv2.EVENT_LBUTTONDOWN):
    print('\nSelected point: ',x,',',y)
    if counter >= 1:   
        print('> Difference from previous point: ',x-prev_point[0],',',y-prev_point[1])
    prev_point = [x,y]
    colorsBGR = res_image[y, x]
    # reversing the OpenCV BGR format to RGB format
    colorsRGB = tuple(reversed(colorsBGR)) 
    print("> RGB Value: {}".format(colorsRGB))
    counter = counter + 1

# converting files into JPG format to be able to read them
def conversion(path):
    size = len(path)
    im = Image.open(path)
    rgb_im = im.convert('RGB')
    rgb_im.save(path[:size-4]+'.jpg')

# image resizing
def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]
    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image
    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)
    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))
    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)
    # return the resized image
    return resized

# main
if __name__ == "__main__":
    try:
        root = Tk()
        root.wm_attributes('-alpha', 0)
        filename = fd.askopenfilename()
        path = filename
        size = len(path)

        conversion(path)
        image = cv2.imread(path[:size-4]+'.jpg')
        res_image = image_resize(image, height = 1000)

        cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Image', click_data)
        cv2.imshow('Image',res_image)

        # wait for ESC pressed before quitting
        while (1):
            cv2.setMouseCallback('Image', click_data)
            cv2.imshow('Image',res_image)
            if cv2.waitKey(10) & 0xFF == 27:
                break
    except:
        pass
    
    cv2.destroyAllWindows()

    # clean temporary conversions
    if(path.endswith('.CR2')):
        os.remove(path[:size-4]+'.jpg')
