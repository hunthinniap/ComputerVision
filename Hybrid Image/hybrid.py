import sys
import cv2
import numpy as np

def cross_correlation_2d(img, kernel):
    '''Given a kernel of arbitrary m x n dimensions, with both m and n being
    odd, compute the cross correlation of the given image with the given
    kernel, such that the output is of the same dimensions as the image and that
    you assume the pixels out of the bounds of the image to be zero. Note that
    you need to apply the kernel to each channel separately, if the given image
    is an RGB image.

    Inputs:
        img:    Either an RGB image (height x width x 3) or a grayscale image
                (height x width) as a numpy array.
        kernel: A 2D numpy array (m x n), with m and n both odd (but may not be
                equal).

    Output:
        Return an image of the same dimensions as the input image (same width,
        height and the number of color channels)
    '''
    # TODO-BLOCK-BEGIN
    ker_width, ker_height = kernel.shape
    pad_width, pad_height = ker_width // 2, ker_height // 2
    output = np.zeros(img.shape)

    if len(img.shape) == 2:
        width, height = img.shape
        img_copy = np.zeros((width+ker_width-1, height+ker_height-1))
        img_copy[pad_width:width+pad_width, pad_height:height+pad_height] = img
        for i in range(width):
            for j in range(height):
                temp = kernel * img_copy[i:i+ker_width,j:j+ker_height]
                output[i,j] = temp.sum()
    elif len(img.shape) == 3:
        width, height, channels = img.shape
        img_copy = np.zeros((width+ker_width-1,height+ker_height-1,channels))
        img_copy[pad_width:width + pad_width, pad_height:height + pad_height] = img
        for i in range(width):
            for j in range(height):
                for k in range(channels):
                    temp = kernel * img_copy[i:i+ker_width,j:j+ker_height,k]
                    output[i,j,k]= temp.sum()
    return output


    # TODO-BLOCK-END

def convolve_2d(img, kernel):
    '''Use cross_correlation_2d() to carry out a 2D convolution.

    Inputs:
        img:    Either an RGB image (height x width x 3) or a grayscale image
                (height x width) as a numpy array.
        kernel: A 2D numpy array (m x n), with m and n both odd (but may not be
                equal).

    Output:
        Return an image of the same dimensions as the input image (same width,
        height and the number of color channels)
    '''
    # TODO-BLOCK-BEGIN
    flip_kernel = np.fliplr(np.flipud(kernel))
    return cross_correlation_2d(img,flip_kernel)
    # TODO-BLOCK-END


def gaussian_blur_kernel_2d(sigma, height, width):
    '''Return a Gaussian blur kernel of the given dimensions and with the given
    sigma. Note that width and height are different.

    Input:
        sigma:  The parameter that controls the radius of the Gaussian blur.
                Note that, in our case, it is a circular Gaussian (symmetric
                across height and width).
        width:  The width of the kernel.
        height: The height of the kernel.

    Output:
        Return a kernel of dimensions height x width such that convolving it
        with an image results in a Gaussian-blurred image.
    '''
    # TODO-BLOCK-BEGIN
    output = np.zeros((height, width))

    x = height // 2
    y = width // 2

    constant = 1 / (2 * np.pi * (sigma ** 2))

    for i in range(height):
        for j in range(width):
            temp = ((i - x) ** 2 + (j - y) ** 2)/(2 * sigma ** 2)
            output[i, j] = constant * np.power(np.e, -temp)

    return output / np.sum(output)



    # TODO-BLOCK-END

def low_pass(img, sigma, size):
    '''Filter the image as if its filtered with a low pass filter of the given
    sigma and a square kernel of the given size. A low pass filter supresses
    the higher frequency components (finer details) of the image.

    Output:
        Return an image of the same dimensions as the input image (same width,
        height and the number of color channels)
    '''
    # TODO-BLOCK-BEGIN
    return convolve_2d(img,gaussian_blur_kernel_2d(sigma,size,size))
    # TODO-BLOCK-END

def high_pass(img, sigma, size):
    '''Filter the image as if its filtered with a high pass filter of the given
    sigma and a square kernel of the given size. A high pass filter suppresses
    the lower frequency components (coarse details) of the image.

    Output:
        Return an image of the same dimensions as the input image (same width,
        height and the number of color channels)
    '''
    # TODO-BLOCK-BEGIN
    return img - low_pass(img,sigma,size)
    # TODO-BLOCK-END

def create_hybrid_image(img1, img2, sigma1, size1, high_low1, sigma2, size2,
        high_low2, mixin_ratio, scale_factor):
    '''This function adds two images to create a hybrid image, based on
    parameters specified by the user.'''
    high_low1 = high_low1.lower()
    high_low2 = high_low2.lower()

    if img1.dtype == np.uint8:
        img1 = img1.astype(np.float32) / 255.0
        img2 = img2.astype(np.float32) / 255.0

    if high_low1 == 'low':
        img1 = low_pass(img1, sigma1, size1)
    else:
        img1 = high_pass(img1, sigma1, size1)

    if high_low2 == 'low':
        img2 = low_pass(img2, sigma2, size2)
    else:
        img2 = high_pass(img2, sigma2, size2)

    img1 *=  (1 - mixin_ratio)
    img2 *= mixin_ratio
    hybrid_img = (img1 + img2) * scale_factor
    return (hybrid_img * 255).clip(0, 255).astype(np.uint8)

