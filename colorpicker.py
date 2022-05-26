from cv2 import cv2
from PIL import Image
from gooey import Gooey, GooeyParser
import pyperclip
import os

# -- obsolete
def pickerRGB(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # checks mouse moves
        colorsBGR = image[y, x]
        colorsRGB = tuple(reversed(colorsBGR)) #Reversing the OpenCV BGR format to RGB format
        pyperclip.copy(colorsRGB)
        print("RGB values copied to clipboard!")
        print("RGB value at ({},{}):{} ".format(x,y,colorsRGB))


def conversion(path):
    size = len(path)
    im = Image.open(path)
    rgb_im = im.convert('RGB')
    rgb_im.save(path[:size-4]+'.jpg')


# -- inizializzazione Gooey
@Gooey(
    program_name='Color Checker',       # Defaults to script name
    default_size=(500, 350),   # starting size of the GUI
    required_cols=1,           # number of columns in the "Required" section
    optional_cols=1,           # number of columns in the "Optional" section
    clear_before_run=True,
    show_stop_warning=True,
    show_failure_modal=True,
    hide_progress_msg=True,
    dump_build_config=False,   # Dump the JSON Gooey uses to configure itself
    load_build_config=None,    # Loads a JSON Gooey-generated configuration
    monospace_display=False,   # Uses a mono-spaced font in the output screen
    #navigation="TABBED",
    )   
def main():
    path = ''

    parser = GooeyParser(description='Applicazione per estrazione colore')
    subs = parser.add_subparsers(help="commands", dest="command")
    # -- Required parameters section
    fprocessing = subs.add_parser(
        "aaa", prog="aaa",
    ).add_argument_group("")

    fprocessing.add_argument(
        "inputImg",
        metavar="Color checker",
        help="Seleziona il file da esplorare, premi ESC per uscire dal visualizzatore (valori RGB visibili nella parte inferiore del viewer)",
        widget="FileChooser"
    )

    args = vars(parser.parse_args())
    path = args['inputImg']
    size = len(path)

    conversion(path)
    image = cv2.imread(path[:size-4]+'.jpg')
 
    # Create a window and set Mousecallback to a function for that window
    cv2.namedWindow('RGB Picker', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('RGB Picker', 900, 900) 
    cv2.setMouseCallback('RGB Picker', pickerRGB)
    # Do until esc pressed
    while(1):
        cv2.imshow('RGB Picker', image)
        if cv2.waitKey(10) & 0xFF == 27:
            break
    # if esc is pressed, close all windows.
    cv2.destroyAllWindows()
    os.remove(path[:size-4]+'.jpg')


main()