# PyCrop
Images post-production app made in Python for Fondazione Giorgio Cini - Venezia (ARCHiVe Center)

NOTE: There are 2 different versions of the app, according to your operating system (Linux/Windows). Both are still work in progress, especially the latter one.

Required libraries:
 - OpenCV (cv2)
 - Pillow
 - Gooey
 - Matplotlib
 - Numpy

Features:
 - Image conversion (.CR2 to .jpg/.tif)
 - Object detection and crop (with custom padding)
 - Image rotation according to the scanner type
 - Image custom quality compression
 - Color profile application (.pp3)
     - RawTherapee installation is required for this: https://www.rawtherapee.com/
 - White balancing (auto + manual methods through PHP scripts)
     - RGB acquisition for this step is available through the "colorpicker.py" script
 - Json metadata export
 - Image deskew (soon)

"Sample_images" contains some JPGs that can be used for testing the software, while the "examples" folder shows a comparison before-after the processing (image quality has been lowered due to smaller size and easier upload).
