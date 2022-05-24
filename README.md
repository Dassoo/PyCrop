# PyCrop
Images post-production app for Fondazione Giorgio Cini - Venezia (ARCHiVe Center)

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
 - White balancing (auto + manual methods through PHP scripts)
 - Json metadata export
 - Image deskew (soon)

"Sample_images" contains some JPGs that can be used for testing the software, while the "examples" folder shows a comparison before-after the whitebalancing.
