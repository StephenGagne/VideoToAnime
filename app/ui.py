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
- Further Implement Start functionality (AI-integration, frame stitching)
- Implement threading for frame splitting to align with a progress bar
- Refactor to allow for external QSS stylesheets?
'''

import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QProgressBar, QLabel, QTextEdit, QMessageBox
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
import cv2 as cv #import OpenCV library
import os
from importlib.metadata import version
import video_splitter
import ai_image_generation as img_gen
import frame_stitcher as stitcher

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(200, 200, 400, 450)  #set size and position of window
        self.setWindowTitle("Project - Group 8")
        self.setStyleSheet("background-color: #add8e6;") #background color: light blue
        self.__file = None
        self.__frame_total = 0
        self.initUI()

    def initUI(self):        
        #upload button
        self.uploadButton = QtWidgets.QPushButton(self)
        self.uploadButton.setGeometry(20, 10, 360, 50)
        self.uploadButton.setText("Upload")
        self.uploadButton.clicked.connect(self.uploadClicked)
        self.uploadButton.setStyleSheet("background-color: #f5f5f5; color:black;")
        self.uploadButton.setToolTip("Upload a video to be processed")

        #start button
        self.startButton = QtWidgets.QPushButton(self)
        self.startButton.setGeometry(205, 65, 175, 50)
        self.startButton.setText("Start")
        self.startButton.clicked.connect(self.startClicked)
        self.startButton.setStyleSheet("background-color: darken(foreground, 20);")
        self.startButton.setEnabled(False)
        self.startButton.setToolTip("Initiate the conversion process")
        
        #play button
        self.playButton = QtWidgets.QPushButton(self)
        self.playButton.setGeometry(20, 65, 175, 50)
        self.playButton.setText("Play Video")
        self.playButton.clicked.connect(self.playClicked)
        self.playButton.setStyleSheet("background-color: darken(foreground, 20);")
        self.playButton.setEnabled(False)
        self.playButton.setToolTip("Play the currently uploaded video")
        
        #prompt boxes
        self.positive_prompt_text = QLabel(self)
        self.positive_prompt_text.setGeometry(20, 120, 105, 50)
        self.positive_prompt_text.setText("Positive Prompts: ")
        self.positive_prompt = QTextEdit(self)
        self.positive_prompt.setGeometry(135, 120, 245, 50)
        self.negative_prompt_text = QLabel(self)
        self.negative_prompt_text.setGeometry(20, 175, 105, 50)
        self.negative_prompt_text.setText("Negative Prompts: ")
        self.negative_prompt = QTextEdit(self)
        self.negative_prompt.setGeometry(135, 175, 245, 50)
        
        #playback progress -= maybe unneeded?
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setGeometry(20, 230, 360, 50)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setFormat("Playback - %p%")
        self.progress_bar.setVisible(False)

        #split progress widgets
        self.split_prog_icon = QLabel(self)
        self.split_prog_icon.setGeometry(120, 305, 20, 20)
        self.split_prog_icon.setPixmap(QPixmap("assets\\loading.png").scaled(20,20))
        self.split_prog_icon.setVisible(False)
        self.split_prog_text = QLabel(self)
        self.split_prog_text.setGeometry(160, 305, 200, 20)
        self.split_prog_text.setText("Splitting frames...")
        self.split_prog_text.setVisible(False)
        
        #imggen progress widgets
        self.gen_prog_icon = QLabel(self)
        self.gen_prog_icon.setGeometry(120, 350, 20, 20)
        self.gen_prog_icon.setPixmap(QPixmap("assets\\loading.png").scaled(20,20))
        self.gen_prog_icon.setVisible(False)
        self.gen_prog_text = QLabel(self)
        self.gen_prog_text.setGeometry(160, 350, 200, 20)
        self.gen_prog_text.setText("Generating frames...")
        self.gen_prog_text.setVisible(False)
        
        #stitch progress widgets
        self.stitch_prog_icon = QLabel(self)
        self.stitch_prog_icon.setGeometry(120, 395, 20, 20)
        self.stitch_prog_icon.setPixmap(QPixmap("assets\\loading.png").scaled(20,20))
        self.stitch_prog_icon.setVisible(False)
        self.stitch_prog_text = QLabel(self)
        self.stitch_prog_text.setGeometry(160, 395, 200, 20)
        self.stitch_prog_text.setText("Stiching video back together...")
        self.stitch_prog_text.setVisible(False)
        
        #properties
        self.properties = QtWidgets.QPushButton(self)
        self.properties.setGeometry(20, 420, 360, 25)
        self.properties.setText("Project Properties")
        self.properties.clicked.connect(self.showProperties)
        self.properties.setStyleSheet("background-color: #f5f5f5; color:black;")
        self.properties.setToolTip("Show project properties, including the current video and system properties")
        

    def showProperties(self):
        current_qt = version('PyQt5')
        current_cv = cv.__version__
        current_py = str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2])
        if self.__file == None:
            current_project = "No project uploaded yet."
        else:
            current_project = self.__file
        if self.positive_prompt.toPlainText() == "":
            current_prompt_p = 'No positive prompts selected.'
        else:
            current_prompt_p = self.positive_prompt.toPlainText()
        if self.negative_prompt.toPlainText() == "":
            current_prompt_n = "No negative prompts selected."
        else:
            current_prompt_n = self.negative_prompt.toPlainText()  
        properties_text = "Current Project: \n\t" + current_project + "\nCurrent Positive Prompts: \n\t" + current_prompt_p + "\nCurrent Negative Prompts: \n\t" + current_prompt_n
        versions_text = "Current Python Version: " + current_py + "\nCurrent PyQt Version: " + current_qt + "\nCurrent OpenCV Version: " + current_cv
        props = QMessageBox()
        props.setWindowTitle("Project Properties")
        props.setIcon(QMessageBox.Information)
        props.setText(properties_text)
        props.setDetailedText(versions_text)
        props.exec_()

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
        if self.positive_prompt.toPlainText() == "":
            errdlg = QMessageBox()
            errdlg.setWindowTitle("Error - No Positive Prompts!")
            errdlg.setIcon(QMessageBox.Critical)
            errdlg.setText("Please add positive prompts before trying again!")
            errdlg.exec_()
            return
        if self.__file is not None:
            self.start_thread = QThread(self)
            self.start_worker = Worker(self.splitFrames)
            self.start_worker.moveToThread(self.start_thread)
            self.start_thread.started.connect(self.start_worker.run)
            self.start_thread.start()
                
    def splitFrames(self):
        self.split_prog_icon.setVisible(True)
        self.split_prog_text.setVisible(True)
        video_splitter.split(self.__file)
        self.splitFinished()
        self.generateFrames()
        self.stitchVideo()
    
    def splitFinished(self):
        self.split_prog_icon.setPixmap(QPixmap("assets\\check.png").scaled(20,20))
        self.split_prog_text.setText("Finished Splitting Frames!")
        self.split_prog_text.setStyleSheet("color: green")
    
    def generateFrames(self):
        self.gen_prog_icon.setVisible(True)
        self.gen_prog_text.setVisible(True)
        if self.positive_prompt.toPlainText() == "":
            prompt_p = ""
        else:
            prompt_p = self.positive_prompt.toPlainText()
        if self.negative_prompt.toPlainText() == "":
            prompt_n = ""
        else:
            prompt_n = self.negative_prompt.toPlainText()
        img_gen.ai_generate(prompt_p, prompt_n)
        self.genFinished()
    
    def genFinished(self):
        self.gen_prog_icon.setPixmap(QPixmap("assets\\check.png").scaled(20,20))
        self.gen_prog_text.setText("Finished Generating Frames!")
        self.gen_prog_text.setStyleSheet("color: green")
    
    def stitchVideo(self):
        self.stitch_prog_icon.setVisible(True)
        self.stitch_prog_text.setVisible(True)
        animated_video_name = self.__file.split("/")[-1].split(".")[0]
        stitcher.stitch_frames(animated_video_name)
        self.stitchFinished()
    
    def stitchFinished(self):
        self.stitch_prog_icon.setPixmap(QPixmap("assets\\check.png").scaled(20,20))
        self.stitch_prog_text.setText("Finished Stitching Video!")
        self.stitch_prog_text.setStyleSheet("color: green")
    
    def playClicked(self):
        print("Play button clicked!")
        if self.__file is not None:
            self.play_thread = QThread(self)
            self.play_worker = Worker(self.playVideo)
            self.play_worker.moveToThread(self.play_thread)
            self.play_thread.started.connect(self.play_worker.run)
            self.play_thread.start()
            
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
    
class Worker(QObject):
    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        self.function(*self.args, **self.kwargs)
        
def window():
        app = QApplication(sys.argv)
        win = MyWindow()
        win.show()
        sys.exit(app.exec_())

window()
