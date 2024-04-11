"""
This script implement PyQt5 GUI application for uploading
and displaying video using OpenCV
Author: Vy Chau
Date: 04.04.2024
"""

'''
Current known issues:
- After playback (natural end or interruption), program will terminate instead of waiting for another button press
- Widget geometry is hard-coded, should be programmatically determined
'''
'''
Future Plans:
- Delink Upload from Playback, Upload's sole role will be to navigate to a file, validate it, and store it for use
  in other signals
- Implement Start functionality (frame splitting, AI-integration, frame stitching)
- Implement threading for frame splitting to align with a progress bar
- Refactor to allow for external QSS stylesheets?
'''

import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QProgressBar
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *
import cv2 as cv #import OpenCV library
import os
from importlib.metadata import version
import video_splitter_2

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(200, 200, 400, 280)  #set size and position of window
        self.setWindowTitle("Project - Group 8")
        self.setStyleSheet("background-color: #add8e6;") #background color: light blue
        self.threadpool = QThreadPool()
        self.__file = None
        self.__frame_total = 0
        self.initUI()

    def initUI(self):
        current_qt = version('PyQt5')
        current_cv = cv.__version__
        current_versions = 'Current PyQt Version: ' + current_qt + '\nCurrent OpenCV Version: ' + current_cv
        self.dependency_versions = QtWidgets.QLabel(current_versions, self)
        self.dependency_versions.setGeometry(5, 0, 400, 40)
        
        #upload button
        self.uploadButton = QtWidgets.QPushButton(self)
        self.uploadButton.setGeometry(20, 45, 360, 50)
        self.uploadButton.setText("Upload")
        self.uploadButton.clicked.connect(self.uploadClicked)
        self.uploadButton.setStyleSheet("background-color: #f5f5f5; color:black;")

        #start button
        self.startButton = QtWidgets.QPushButton(self)
        self.startButton.setGeometry(205, 100, 175, 50)
        self.startButton.setText("Start")
        #self.startButton.move(210, 20)
        self.startButton.clicked.connect(self.startClicked)
        self.startButton.setStyleSheet("background-color: darken(foreground, 20);")
        self.startButton.setEnabled(False)
        
        self.playButton = QtWidgets.QPushButton(self)
        self.playButton.setGeometry(20, 100, 175, 50)
        self.playButton.setText("Play Video")
        self.playButton.clicked.connect(self.playClicked)
        self.playButton.setStyleSheet("background-color: darken(foreground, 20);")
        self.playButton.setEnabled(False)
        
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setGeometry(20, 155, 360, 50)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setFormat("Playback - %p%")
        self.progress_bar.setVisible(False)
        
        self.split_prog_bar = QtWidgets.QProgressBar(self)
        self.split_prog_bar.setGeometry(20, 210, 360, 50)
        self.split_prog_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.split_prog_bar.setFormat("Splitting Frames - %p%")
        self.split_prog_bar.setVisible(False)

    def uploadClicked(self):   
        options = QFileDialog.Options()
        file_types = "Video Files (*.mp4 *.avi *.mov);;All Files (*)"
        file_name, _ = QFileDialog.getOpenFileName(self,"Select Video File", "", file_types, options=options)
        self.__file = file_name
        
        cap = cv.VideoCapture(file_name)
        self.__frame_total = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        self.playButton.setEnabled(True)
        self.startButton.setEnabled(True)
        self.playButton.setStyleSheet("background-color: #f5f5f5; color: black;")
        self.startButton.setStyleSheet("background-color: #f5f5f5; color: black;")
        
    def startClicked(self):
        if self.__file is not None:
            worker = Worker(self.splitFrames)
            self.threadpool.start(worker)
            
        self.split_prog_bar.setVisible(True)
        folder = os.getcwd() + '\\originalFrames'
        # TODO Logic for tracking files being created for feeding into progbar value
          
    def splitFrames(self):
        video_splitter_2.split(self.__file)
    
    def playClicked(self):
        print("Play button clicked!")
        if self.__file is not None:
            worker = Worker(self.playVideo)
            self.threadpool.start(worker)
            
    def playVideo(self):
        file_name = self.__file
        if file_name:
            cap = cv.VideoCapture(file_name)
            if not cap.isOpened():
                print("Error: Could not open video file")
                return

            frame_rate = cap.get(cv.CAP_PROP_FPS)
            if frame_rate == 0:
                print("Warning: Unable to determine frame rate. Using default delay.")
                delay = 30
            else:
                delay = int(500 / frame_rate)
            frame_count = 0
            
            self.__frame_total = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(self.__frame_total)

            video_name = file_name.split("/")[-1]
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame_count += 1
                    print("Processing frame", frame_count)
                    self.progress_bar.setValue(frame_count)
                    
                    frame_h, frame_w = frame.shape[:2]
                    if 720 < frame_h or 1280 < frame_w: # resizing the video down to 720x1280 if it's larger
                        scaling = 720 / float(frame_h)
                        if 1280 / float(frame_w) < scaling:
                            scaling = 1280 / float(frame_w)
                        frame = cv.resize(frame, None, fx = scaling, fy = scaling, interpolation = cv.INTER_AREA) 
                    
                    window_name = 'Playing Video - ' + video_name
                    cv.imshow(window_name, frame)
                    if cv.waitKey(delay) == ord('q'):
                        break
                    if cv.getWindowProperty(window_name, cv.WND_PROP_VISIBLE) < 1: # allows for the video to be closed before finishing
                        self.progress_bar.setVisible(False)
                        break
                else:
                    break
            cap.release()
            cv.destroyAllWindows()
    
class Worker(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
    
    @pyqtSlot()
    def run(self):
        self.function(*self.args, **self.kwargs)
        
def window():
        app = QApplication(sys.argv)
        win = MyWindow()
        win.show()
        sys.exit(app.exec_())

window()
