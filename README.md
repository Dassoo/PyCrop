# PyCrop

Images post-production app made in Python for Fondazione Giorgio Cini - Venezia (ARCHiVe Center)

## Features

- Image conversion (.CR2 to .jpg/.tif)
- Object detection and crop (with custom padding)
- Image rotation according to the scanner type
- Image custom quality compression
- Color profile application (.pp3)
- White balancing
- Json metadata export


## Installation

NOTE: There are 2 different versions of the app, according to your operating system (Linux/Windows). Both are still work in progress, especially the latter one.

Clone the project

```bash
  git clone https://github.com/Dassoo/PyCrop
```

Go to the project directory

```bash
  cd PyCrop-master
```

Install dependencies

```bash
  pip install opencv-python
  pip install pillow
  pip install gooey
  pip install matplotlib
  pip install numpy
```

Install RawTherapee: https://www.rawtherapee.com/

Run the right OS version of the app

```bash
  python pyCrop_linux.py
  OR
  python pyCrop_win.py
```


## Usage/Examples

"Sample_images" contains some JPGs that can be used for testing the software, while the "examples" folder shows a comparison before-after the processing (image quality has been lowered due to smaller size and easier upload).

Creating a dedicated output folder is recommended.

You can access the colorpicker script to take the white RGB for the whitebalancing given an image

```bash
  python colorpicker.py
```

## Screenshots

![source1](https://github.com/Dassoo/PyCrop/blob/master/examples/source1.jpg)

<img src="https://github.com/Dassoo/PyCrop/blob/master/examples/source1.jpg" width="128"/>



