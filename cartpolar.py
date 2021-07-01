import numpy as np
import cv2

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class MainWindow(QMainWindow):
    def mousePressEvent(self, e):
        print("mouse pressed at " + str(e.pos()))

# Menu bar functions

def open_file():
    global leftImage, rightImage, leftImageLabel, rightImageLabel
    path = QFileDialog.getOpenFileName(window, "Open", filter="Image Files (*.png *.jpg *.bmp)")[0]
    if path:
        leftImage = cv2.imread(path)
        rightImage = cartesianToPolar(leftImage, (540,540))
        updateImage(leftImageLabel, leftImage)
        updateImage(rightImageLabel, rightImage)

def save_image():
    global rightImage
    dialog = QFileDialog()
    dialog.setAcceptMode(QFileDialog.AcceptSave)
    dialog.setDefaultSuffix("png")
    if dialog.exec_() == QDialog.Accepted:
        path = dialog.selectedFiles()[0]
        print("Saved file " + path)
        cv2.imwrite(path, rightImage)
    else:
        print("Cancelled")

def show_about_dialog():
    text = "<center>" \
           "<h2>CartPolar</h2>" \
           "<p>CartPolar is a program that converts images " \
           "from polar coordinates to cartesian and vice-versa.</p>" \
           "<p>Created by <a href=\"https://inf.ufrgs.br/~awcampana\">Artur Waquil Campana</a></p>" \
           "<a href=\"https://github.com/arturwaquil/CartPolar\">See this project on GitHub</a>" \
           "</center>"
    QMessageBox.about(window, "About CartPolar", text)

# End of menu bar functions

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

def updateImage(label, image):
    label.setPixmap(cvToQt(image).scaledToHeight(500))

if __name__ == "__main__":

    app = QApplication([])
    app.setApplicationDisplayName("CartPolar")
    window = MainWindow()
    window.setWindowTitle("Polar to Cartesian")

    # Layout with the before image (left) and the after image (right)
    leftImageLabel = QLabel(window)
    rightImageLabel = QLabel(window)
    imgsLayout = QHBoxLayout()
    imgsLayout.addWidget(leftImageLabel)
    imgsLayout.addWidget(rightImageLabel)

    mainWidget = QWidget()
    mainWidget.setLayout(imgsLayout)
    window.setCentralWidget(mainWidget)


    # Menu bar definitions

    menu = window.menuBar().addMenu("&File")

    open_action = QAction("&Open image")
    open_action.triggered.connect(open_file)
    open_action.setShortcut(QKeySequence.Open)
    menu.addAction(open_action)

    save_action = QAction("&Save resulting image")
    save_action.triggered.connect(save_image)
    save_action.setShortcut(QKeySequence.Save)
    menu.addAction(save_action)

    close_action = QAction("&Close")
    close_action.triggered.connect(window.close)
    close_action.setShortcut(QKeySequence.fromString("Ctrl+Q"))
    menu.addAction(close_action)


    help_menu = window.menuBar().addMenu("&Help")

    about_action = QAction("&About")
    about_action.triggered.connect(show_about_dialog)
    about_action.setShortcut(QKeySequence.fromString("F1"))
    help_menu.addAction(about_action)

    # End of menu bar definitions


    # OpenCV images
    leftImage = getExampleImage()
    rightImage = cartesianToPolar(leftImage, (540,540))

    updateImage(leftImageLabel, leftImage)
    updateImage(rightImageLabel, rightImage)

    window.show()
    app.exec_()
