#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author: Jacob Kosberg
"""

from SaveState import guisave, guirestore
from PyQt4 import QtGui, QtCore, uic

import time
import os
import argparse
import sys

class MainWindow(QtGui.QMainWindow):
    """MainWindow initializes UI objects like buttons, text/check/spin boxes, etc."""
    def __init__(self, worker):
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi('ui/main.ui', self)
        self.setWindowTitle("Timelapse Workbench")
        self.setFixedSize(self.size())
        self.settings = QtCore.QSettings('ui/main.ini', QtCore.QSettings.IniFormat)
        guirestore(self)
        self.worker = worker
        self.wireUiElements()
        self.setInitValues()

    def setInitValues(self):
        self.worker.setImagesPath(str(self.imagesPath.text()))
        self.worker.setFPS(self.fpsSpinBox.value())
        self.worker.setOutputPath(str(self.outputPath.text()))

    def wireUiElements(self):
        # Camera Settings/Parameters Button
        self.renderButton.clicked.connect(
            lambda: self.worker.actionQueue.append(self.worker.render))

        # FPS
        self.fpsSpinBox.valueChanged.connect(
            lambda: self.worker.setFPS(self.fpsSpinBox.value()))

        # Capture path
        self.imagesPath.textChanged.connect(
            lambda: self.worker.setImagesPath(str(self.imagesPath.text())))

        # Output path
        self.outputPath.textChanged.connect(
            lambda: self.worker.setOutputPath(str(self.outputPath.text())))

        # Progress Bar
        self.worker.renderProgress.connect(self.progressBar.setValue)



    def closeEvent(self, event):
        self.worker.running = False
        guisave(self)
        event.accept()

class Worker(QtCore.QThread):
    """
    QT thread for activating cameras, capturing and scaling images.
    self.cameras is actually a list of CameraSettings, which act as
    camera managers.
    """
    renderProgress = QtCore.pyqtSignal(int)
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.running = True
        self.actionQueue = []


    def render(self):
        print("----- Rendering")
        import timelapse_creator
        timelapse_creator.create_timelapse(self.imagesPath, self.fps, self.outputPath, 0, 1, self.renderProgress)
        self.renderProgress.emit(100)
        print("----- Done!")


    def run(self):
        while self.running:
            self.idle()
        self.kill()

    def idle(self):
        while self.actionQueue:
            self.actionQueue.pop(0)()

    def createPathIfNotExists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def assertPathNotNull(self, path):
        if path in [None, ""]:
            raise ValueError("Path cannot be empty!")

    def captureImage(self):
        #filename = self.getImageFilepath(self.imagesPath, cameraSettings.deviceNameStr)
        cv2.imwrite(filename, frame)
        return filename

    def getImageFilepath(self, path, deviceName):
        """
        Creates file path under 'deviceName' folder in parent images path.
        Uses date and time as filename. Ex: '2017-08-08_10-29-57.png'
        """
        self.assertPathNotNull(path)
        newPath = os.path.join(path, str(deviceName))
        self.createPathIfNotExists(newPath)
        return os.path.join(newPath, self.getDateString() + ".png")

    def getDateString(self):
        return time.strftime("%Y-%m-%d_%H-%M-%S")

    def setImagesPath(self, path):
        self.imagesPath = path

    def setOutputPath(self, path):
        self.outputPath = path

    def setFPS(self, fps):
        self.fps = fps

    def kill(self):
        self.running = False

def main():
    parser = argparse.ArgumentParser(
        description="UI utility for rendering time lapses from PNG sequences.")
    args = parser.parse_args()

    app = QtGui.QApplication(['TimelapseWorkbench'])

    worker = Worker()
    worker.start()
    mainWindow = MainWindow(worker)
    mainWindow.show()
    app.exec_()
    time.sleep(2)
    app.quit()

if __name__ == '__main__':
    main()