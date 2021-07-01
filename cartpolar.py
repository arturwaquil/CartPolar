from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QHBoxLayout, \
                            QLabel, QDialog, QFileDialog, QMessageBox, QAction
from PyQt5.QtGui import QPixmap, QImage, QKeySequence
import numpy as np
import cv2
from conversions import *


class GUI:
    def __init__(self):

        self.app = QApplication([])
        self.app.setApplicationDisplayName("CartPolar")
        self.window = QMainWindow()
        self.window.setWindowTitle("Polar to Cartesian")

        # Layout with the before image (left) and the after image (right)
        self.leftImageLabel = self.QLabelMouseDetection(self.window, self)
        self.rightImageLabel = QLabel(self.window)
        imgsLayout = QHBoxLayout()
        imgsLayout.addWidget(self.leftImageLabel)
        imgsLayout.addWidget(self.rightImageLabel)

        mainWidget = QWidget()
        mainWidget.setLayout(imgsLayout)
        self.window.setCentralWidget(mainWidget)
        self.addMenus()

        self.updateOriginalImage(self.getExampleImage())

    def run(self):
        self.window.show()
        self.app.exec_()

    # Put the OpenCV image passed in the PyQt label passed
    def updateLabel(self, label, image):

        # Convert OpenCV image (numpy array) to QPixmap
        def cvToQt(img):
            height, width, _ = img.shape
            bytesPerLine = 3 * width
            return QPixmap(QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped())

        label.setPixmap(cvToQt(image).scaled(500, 500))

    # Update the original (left) picture
    def updateOriginalImage(self, image):
        self.leftImage = image
        self.updateLabel(self.leftImageLabel, self.leftImage)
        self.updateConvertedImage((0,0))

    # Update the converted (right) picture
    def updateConvertedImage(self, center):
        self.rightImage = cartesianToPolar(self.leftImage, center)
        self.updateLabel(self.rightImageLabel, self.rightImage)

    # Generate circles pattern in an OpenCV image
    def getExampleImage(self):
        img = np.zeros((1080,1080,3), np.uint8)
        transitions = [264, 231, 194, 163, 129, 100, 72, 50, 29, 11]
        for i, transition in enumerate(transitions):
            cv2.circle(img, (540,540), transition, [(255,255,255),(0,0,0)][i%2], -1)
        return img

    def addMenus(self):

        self.menu = self.window.menuBar().addMenu("&File")

        self.open_action = QAction("&Open image")
        self.open_action.triggered.connect(self.open_file)
        self.open_action.setShortcut(QKeySequence.Open)
        self.menu.addAction(self.open_action)

        self.save_action = QAction("&Save resulting image")
        self.save_action.triggered.connect(self.save_image)
        self.save_action.setShortcut(QKeySequence.Save)
        self.menu.addAction(self.save_action)

        self.close_action = QAction("&Close")
        self.close_action.triggered.connect(self.window.close)
        self.close_action.setShortcut(QKeySequence.fromString("Ctrl+Q"))
        self.menu.addAction(self.close_action)


        self.help_menu = self.window.menuBar().addMenu("&Help")

        self.about_action = QAction("&About")
        self.about_action.triggered.connect(self.show_about_dialog)
        self.about_action.setShortcut(QKeySequence.fromString("F1"))
        self.help_menu.addAction(self.about_action)

    def open_file(self):
        path = QFileDialog.getOpenFileName(self.window, "Open", filter="Image Files (*.png *.jpg *.bmp)")[0]
        if path:
            self.updateOriginalImage(cv2.imread(path))

    def save_image(self):
        global rightImage
        dialog = QFileDialog()
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDefaultSuffix("png")
        if dialog.exec_() == QDialog.Accepted:
            cv2.imwrite(dialog.selectedFiles()[0], rightImage)

    def show_about_dialog(self):
        text = "<center>" \
            "<h2>CartPolar</h2>" \
            "<p>CartPolar is a program that converts images " \
            "from polar coordinates to cartesian and vice-versa.</p>" \
            "<p>Created by <a href=\"https://inf.ufrgs.br/~awcampana\">Artur Waquil Campana</a></p>" \
            "<a href=\"https://github.com/arturwaquil/CartPolar\">See this project on GitHub</a>" \
            "</center>"
        QMessageBox.about(self.window, "About CartPolar", text)

    # Subclass of QLabel created to detect when the mouse is pressed
    class QLabelMouseDetection(QLabel):

        def __init__(self, window, gui):
            super().__init__(window)
            self.gui = gui

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
            mousePos = self.qPointToTuple(e.pos())
            labelSize = self.qSizeToTuple(self.size())
            ratio = self.getTupleRatio(mousePos, labelSize)

            imgsize = self.gui.leftImage.shape
            imgsize = (imgsize[0], imgsize[1])

            newCenter = self.scaleRatio(ratio, imgsize)
            self.gui.updateConvertedImage(newCenter)

if __name__ == "__main__":
    GUI().run()