from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QHBoxLayout, \
                            QLabel, QDialog, QFileDialog, QMessageBox, QAction
from PyQt5.QtGui import QPixmap, QImage, QKeySequence
import numpy as np
import cv2


# Subclass of QLabel created to detect when the mouse is pressed
class QLabelMouseDetection(QLabel):

    def getTupleRatio(self, t1, t2):
        return (t1[0]/t2[0], t1[1]/t2[1])

    def scaleRatio(self, ratio, imgsize):
        return (int(round(ratio[0]*imgsize[0])), int(round(ratio[1]*imgsize[1])))

    def qPointToTuple(self, point):
        return (point.x(), point.y())

    def qSizeToTuple(self, size):
        return (size.width(), size.height())

    # Detect when mouse is pressed and update right image
    def mousePressEvent(self, e):
        global leftImage, rightImage, rightImageLabel

        mousePos = self.qPointToTuple(e.pos())
        labelSize = self.qSizeToTuple(self.size())
        ratio = self.getTupleRatio(mousePos, labelSize)

        imgsize = leftImage.shape
        imgsize = (imgsize[0], imgsize[1])

        newCenter = self.scaleRatio(ratio, imgsize)
        rightImage = cartesianToPolar(leftImage, newCenter)
        updateImage(rightImageLabel, rightImage)


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
        cv2.imwrite(dialog.selectedFiles()[0], rightImage)

def show_about_dialog():
    text = "<center>" \
           "<h2>CartPolar</h2>" \
           "<p>CartPolar is a program that converts images " \
           "from polar coordinates to cartesian and vice-versa.</p>" \
           "<p>Created by <a href=\"https://inf.ufrgs.br/~awcampana\">Artur Waquil Campana</a></p>" \
           "<a href=\"https://github.com/arturwaquil/CartPolar\">See this project on GitHub</a>" \
           "</center>"
    QMessageBox.about(window, "About CartPolar", text)


# Generate circles pattern in an OpenCV image
def getExampleImage():
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
    label.setPixmap(cvToQt(image).scaled(500, 500))

if __name__ == "__main__":

    app = QApplication([])
    app.setApplicationDisplayName("CartPolar")
    window = QMainWindow()
    window.setWindowTitle("Polar to Cartesian")

    # Layout with the before image (left) and the after image (right)
    leftImageLabel = QLabelMouseDetection(window)
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



    # OpenCV images
    leftImage = getExampleImage()
    rightImage = cartesianToPolar(leftImage, (540,540))

    updateImage(leftImageLabel, leftImage)
    updateImage(rightImageLabel, rightImage)

    window.show()
    app.exec_()
