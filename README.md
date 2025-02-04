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

NOTE: There are 2 different versions of the app, according to your operating system (Linux/Windows). Both are still work in progress, especially the latter one (color profile and whitebalance are WIP on Windows due to different compatibility).

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
  python pyCrop_{OS_VERSION}.py
```


## Usage/Examples

"Sample_images" contains some JPGs that can be used for testing the software, while the "examples" folder shows a comparison before-after the processing (image quality has been lowered due to smaller size and easier upload).

Creating a dedicated output folder is recommended.

You can access the colorpicker script to take the white RGB for the whitebalancing given an image

```bash
  python colorpicker.py
```

To use the color profile section, you must have a generated .pp3 file (you can create a custom/test one with RawTherapee, if you already don't have one).


## Screenshots

### Before
![source1](https://github.com/Dassoo/PyCrop/blob/master/examples/source1.jpg)
### After
![result1](https://github.com/Dassoo/PyCrop/blob/master/examples/result1.jpg)

---

### Before
![source2](https://github.com/Dassoo/PyCrop/blob/master/examples/source2.jpg)
### After
![result2](https://github.com/Dassoo/PyCrop/blob/master/examples/result2.jpg)





