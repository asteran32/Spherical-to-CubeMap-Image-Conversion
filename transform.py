# !/usr/bin/env python
import math
import cv2
from PIL import Image
import numpy as np
import os

def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None

def imwrite(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
def cvt_cubemap(input_path, output_dir, size:int=1024):
    """
    Converts an equirectangular image to a cube map.

    Parameters:
    input (str): Path of the input image.
    output_dir (str): Path where the output image will be saved.
    size (int, optional): Side size of the output image, default is 1024.

    This function calculates the 3D coordinates for each pixel, converts these to spherical coordinates,
    and maps these to the original equirectangular image. The result is saved to the output path.
    """
    half_size = size >> 1

    im = imread(input_path)
    if im is None:
        return
    
    side_im = np.zeros((size, size), np.uint8)
    color_side = np.zeros((size, size, 3), np.uint8)

    # If you want to get up and down side of image, range(6)
    for i in range(4):

        #  This is numpy's way of visiting each point in an ndarray, I guess its fast...
        it = np.nditer(side_im, flags=['multi_index'], op_flags=['readwrite'])
        while not it.finished:
            # Axis
            axA = it.multi_index[0]
            axB = it.multi_index[1]

            # Color is an axis, so we visit each point 3 times for R,G,B actually...
            # Here for each face we decide what each axis represents, x, y or z. 
            z = -axA + half_size
            
            if i == 0:
                x = half_size
                y = -axB + half_size

            elif i == 1:
                x = -half_size
                y = axB - half_size

            elif i == 2:
                x = axB - half_size
                y = half_size

            elif i == 3:
                x = -axB + half_size
                y = -half_size

            elif i == 4:
                z = half_size
                x = axB - half_size
                y = axA - half_size

            elif i == 5:
                z = -half_size
                x = axB - half_size
                y = -axA + half_size
        
            # Now that we have x,y,z for point on plane, convert to spherical.
            r = math.sqrt(float(x*x + y*y + z*z))
            theta = math.acos(float(z) / r)
            phi = -math.atan2(float(y) , x)
            
            # Now that we have spherical, decide which pixel from the input image we want.
            ix = int((im.shape[1] - 1) * phi / ( 2 * math.pi))
            iy = int((im.shape[0] - 1) * (theta) / math.pi)

            # This is faster than accessing the whole tuple.
            r = im[iy, ix, 0]
            g = im[iy, ix, 1]
            b = im[iy, ix, 2]

            color_side[axA, axB, 0] = r
            color_side[axA, axB, 1] = g
            color_side[axA, axB, 2] = b

            it.iternext()

        # Save output image using prefix
        # 20210604\강서-012-001\PIC_20210525_102058_2.jpg -> pic-강서-012-001-1.jpg
        split_list = input_path.split('\\')
        output_fname = 'pic-' + split_list[-2] + split_list[-1].split('.')[0] + '_%s.jpg' % i
        
        imwrite(os.path.join(output_dir, output_fname), color_side)
        