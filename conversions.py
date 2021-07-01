import numpy as np
import cv2

def getRadius(h,w,cx,cy):
    dA = abs(h-cy)
    dB = abs(h-dA)
    dC = abs(w-cx)
    dD = abs(w-dC)
    return max([dA, dB, dC, dD])

def rotate(img, angle):
    angle = int(angle/90)

    for i in range(angle):
        h,w,_ = img.shape
        temp = np.zeros((w,h,3), np.uint8)
        for j in range(0,h):
            temp[:,h-j-1,:] = img[j,:,:]
        img = temp

    return img

def cartesianToPolar(imgCart, center):
    cx, cy = center
    h, w, _ = imgCart.shape
    radius = getRadius(h,w,cx,cy)
    imgPol = cv2.warpPolar(imgCart, (radius,360), (cx,cy), radius, cv2.INTER_LINEAR+cv2.WARP_FILL_OUTLIERS)
    return rotate(imgPol,90)

def polarToCartesian(imgPol, shape):
    h, w = shape
    cx, cy = int(w/2),int(h/2)
    radius = getRadius(h,w,cx,cy)
    rotImg = rotate(imgPol,270)
    imgCart = cv2.warpPolar(rotImg, (w,h), (cx,cy), radius, cv2.WARP_INVERSE_MAP+cv2.WARP_FILL_OUTLIERS)
    return imgCart
