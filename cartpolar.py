import numpy as np
import cv2

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

def open_file():
    global file_path
    global leftImage, rightImage, leftImageLabel, rightImageLabel
    path = QFileDialog.getOpenFileName(window, "Open")[0]
    if path:
        leftImage = cv2.imread(path)
        leftImageLabel.setPixmap(cvToQt(leftImage).scaledToHeight(500))
        rightImage = cartesianToPolar(leftImage, (540,540))
        rightImageLabel.setPixmap(cvToQt(rightImage).scaledToHeight(500))

def getExampleImage():
    # Generate circles pattern in an OpenCV image
    img = np.zeros((1080,1080,3), np.uint8)
    transitions = [264, 231, 194, 163, 129, 100, 72, 50, 29, 11]
    for i, transition in enumerate(transitions):
        cv2.circle(img, (540,540), transition, [(255,255,255),(0,0,0)][i%2], -1)
    return img

# Convert OpenCV image (numpy array) to QPixmap
def cvToQt(img):
    height, width, _ = img.shape
    bytesPerLine = 3 * width
    return QPixmap(QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped())

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
    imgPol = cv2.warpPolar(imgCart, (radius,360), (cx,cy),
        radius, cv2.INTER_LINEAR+cv2.WARP_FILL_OUTLIERS)
    return rotate(imgPol,90)

if __name__ == "__main__":

    app = QApplication([])
    app.setApplicationDisplayName("CartPolar")

    window = QMainWindow()
    window.setWindowTitle("Polar to Cartesian")

    leftImageLabel = QLabel(window)
    rightImageLabel = QLabel(window)

    leftImage = getExampleImage()
    rightImage = cartesianToPolar(leftImage, (540,540))

    leftImageLabel.setPixmap(cvToQt(leftImage).scaledToHeight(500))
    rightImageLabel.setPixmap(cvToQt(rightImage).scaledToHeight(500))

    layout = QHBoxLayout()
    layout.addWidget(leftImageLabel)
    layout.addWidget(rightImageLabel)

    mainWidget = QWidget()
    mainWidget.setLayout(layout)
    window.setCentralWidget(mainWidget)

    menu = window.menuBar().addMenu("&File")
    open_action = QAction("&Open image")
    open_action.triggered.connect(open_file)
    open_action.setShortcut(QKeySequence.Open)
    menu.addAction(open_action)

    window.show()
    app.exec_()
