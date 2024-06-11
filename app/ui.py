"""
This script implement PyQt5 GUI application for uploading
and displaying video using OpenCV
Author: Zachary and Vy 
Date: 10.06.2024
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
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QApplication, QMainWindow, QFileDialog, QProgressBar, QLabel, QTextEdit, QMessageBox, QDialog, QComboBox, QSpinBox, QPushButton
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
        self.setFixedSize(400, 450)  # Prevent resizing
       # self.setStyleSheet("background-color: #add8e6;") #background color: light blue
        self.__file = None
        self.__frame_total = 0
        self.__current_model = ""
        self.__current_sampler = ""
        self.__current_steps = 5
        self.initUI()

    def initUI(self): 
        #add widget 
        mainWindow = QWidget()
        self.setCentralWidget(mainWindow)

        #create a vertical layout: upload - config - prompts - start - properties
        VLayout = QVBoxLayout()
        mainWindow.setLayout(VLayout)

        #creat a horizontal layout for upload and config buttons
        HLayout = QHBoxLayout()
        mainWindow.setLayout(HLayout)

        #upload button
        self.uploadButton = QPushButton(self)
        self.uploadButton.setGeometry(20, 10, 175, 50)
        self.uploadButton.setText("Upload")
        self.uploadButton.clicked.connect(self.uploadClicked)
        self.uploadButton.setToolTip("Upload a video to be processed")

        #config button
        self.configButton = QPushButton(self)
        self.configButton.setGeometry(205, 10, 175, 50)
        self.configButton.setText("Config")
        self.configButton.clicked.connect(self.configClicked)
        self.configButton.setToolTip("Set or change image generation options")
        
        #prompt boxes
        self.positive_prompt_text = QLabel(self)
        self.positive_prompt_text.setGeometry(20, 65, 105, 50)
        self.positive_prompt_text.setText("Positive Prompts: ")
        self.positive_prompt = QTextEdit(self)
        self.positive_prompt.setGeometry(135, 65, 245, 50)
        self.negative_prompt_text = QLabel(self)
        self.negative_prompt_text.setGeometry(20, 120, 105, 50)
        self.negative_prompt_text.setText("Negative Prompts: ")
        self.negative_prompt = QTextEdit(self)
        self.negative_prompt.setGeometry(135, 120, 245, 50)

        #start button
        self.startButton = QPushButton(self)
        self.startButton.setGeometry(20, 175, 360, 50)
        self.startButton.setText("Start")
        self.startButton.clicked.connect(self.startClicked)
        self.startButton.setEnabled(False)
       # self.startButton.setStyleSheet("background-color: rgba(245, 245, 245, 0.5); color:grey; border-radius: 12px;")
        self.startButton.setToolTip("Initiate the conversion process")

        #split progress widgets
        self.split_prog_icon = QLabel(self)
        self.split_prog_icon.setGeometry(120, 255, 20, 20)
        self.split_prog_icon.setPixmap(QPixmap("assets\\loading.png").scaled(20,20))
        self.split_prog_icon.setVisible(False)
        self.split_prog_text = QLabel(self)
        self.split_prog_text.setGeometry(160, 255, 200, 20)
        self.split_prog_text.setText("Splitting frames...")
        self.split_prog_text.setVisible(False)
        
        #imggen progress widgets
        self.gen_prog_icon = QLabel(self)
        self.gen_prog_icon.setGeometry(120, 310, 20, 20)
        self.gen_prog_icon.setPixmap(QPixmap("assets\\loading.png").scaled(20,20))
        self.gen_prog_icon.setVisible(False)
        self.gen_prog_text = QLabel(self)
        self.gen_prog_text.setGeometry(160, 310, 200, 20)
        self.gen_prog_text.setText("Generating frames...")
        self.gen_prog_text.setVisible(False)
        
        #stitch progress widgets
        self.stitch_prog_icon = QLabel(self)
        self.stitch_prog_icon.setGeometry(120, 365, 20, 20)
        self.stitch_prog_icon.setPixmap(QPixmap("assets\\loading.png").scaled(20,20))
        self.stitch_prog_icon.setVisible(False)
        self.stitch_prog_text = QLabel(self)
        self.stitch_prog_text.setGeometry(160, 365, 200, 20)
        self.stitch_prog_text.setText("Stiching video back together...")
        self.stitch_prog_text.setVisible(False)
        
        #properties
        self.properties = QPushButton(self)
        self.properties.setGeometry(20, 420, 360, 25)
        self.properties.setText("Project Properties")
        self.properties.clicked.connect(self.showProperties)
      #  self.properties.setStyleSheet("background-color: rgba(245, 245, 245, 1); color:black; border-radius: 12px;")
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
            
            
        properties_text = "Current Project: \n\t" + current_project + "\nCurrent Model: \n\t" + self.__current_model + "\nCurrent Sampler: \n\t" + self.__current_sampler + "\nCurrent Steps: \n\t" + str(self.__current_steps) + "\nCurrent Positive Prompts: \n\t" + current_prompt_p + "\nCurrent Negative Prompts: \n\t" + current_prompt_n
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
        if not file_name.endswith(".mp4") or file_name.endswith(".avi") or file_name.endswith(".mov"):
            typeerr = QMessageBox()
            typeerr.setWindowTitle("Error - Incorrect file type!")
            typeerr.setIcon(QMessageBox.Critical)
            typeerr.setText("Please upload a .mp4, .avi, or .mov video file!")
            typeerr.exec_()
            return
        
        self.__file = file_name
        
        cap = cv.VideoCapture(file_name)
        self.__frame_total = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        cap.release()

        self.startButton.setEnabled(True)
      #  self.startButton.setStyleSheet("background-color: rgba(245, 245, 245, 1); color: black; border-radius: 12px;")
      
    def configClicked(self):
        config = QDialog()
      #  config.setStyleSheet("background-color: #add8e6;")
        config.setWindowTitle("Generation Config")
        config.setGeometry(200, 200, 500, 250)
        model_text = QLabel("Select Model: ", config)
        model_text.setGeometry(20, 20, 235, 50)
        sampler_text = QLabel("Select Sampler:", config)
        sampler_text.setGeometry(20, 75, 235, 50)
        steps_text = QLabel("Select Number of Steps: ", config)
        steps_text.setGeometry(20, 125, 235, 50)
        models = os.listdir("../config/Models")
        for model in models:
            model.split("/")[-1]
        samplers = ['euler', 'euler_ancestral', 'heun', 'heunpp2', 'dpm_2', 'spm_2_ancestral', 'lms', 'dpm_fast', 'dpm_adaptive', 'spmpp_2s_ancestral', 'dpmpp_sde', 'dpmpp_sde_gpu', 'dpmpp_2m', 'dpmpp_2m_sde', 'dpmpp_2m_sde_gpu', 'dpmpp_3m_sde', 'dpmpp_3m_sde_gpu', 'ddpm', 'lcm', 'ddim', 'uni_pc', 'uni_pc_bh2']

        model_combo = QComboBox(config)
        model_combo.setGeometry(230, 20, 235, 50)
     #   model_combo.setStyleSheet("background-color: rgba(245, 245, 245, 1);")
        model_combo.addItems(models)
        #self.__current_model = "../config/Models/" + model_combo.currentText()
        
        sampler_combo = QComboBox(config)
     #   sampler_combo.setStyleSheet("background-color: rgba(245, 245, 245, 1);")
        sampler_combo.setGeometry(230, 75, 235, 50)
        sampler_combo.addItems(samplers)
        
        steps_spinner = QSpinBox(config)
     #   steps_spinner.setStyleSheet("background-color: rgba(245, 245, 245, 1);")
        steps_spinner.setGeometry(230, 130, 50, 40)
        steps_spinner.setMinimum(1)
        steps_spinner.setSingleStep(1)
        
        save_config = QPushButton("Save", config)
        save_config.setGeometry(200, 180, 50, 50)
     #   save_config.setStyleSheet("background-color: rgba(245, 245, 245, 1); border-radius: 12px;")
        save_config.clicked.connect(lambda: self.saveConfig(model_combo.currentText(), sampler_combo.currentText(), steps_spinner.value()))
        
        config.exec_()
      
    def saveConfig(self, model, sampler, steps):
         self.__current_model = "../config/Models/" + model
         self.__current_sampler = sampler
         self.__current_steps = steps
      
    def startClicked(self):
        if self.positive_prompt.toPlainText() == "":
            errdlg1 = QMessageBox()
            errdlg1.setWindowTitle("Error - No Positive Prompts!")
            errdlg1.setIcon(QMessageBox.Critical)
            errdlg1.setText("Please add positive prompts before trying again!")
            errdlg1.exec_()
            return
        
        if self.__current_model == None or self.__current_sampler == None:
            errdlg = QMessageBox()
            errdlg.setWindowTitle("Error - Configuration not set!")
            errdlg.setIcon(QMessageBox.Critical)
            errdlg.setText("Please add generation configuration options (Sampler or Model)!")
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
      #  self.split_prog_text.setStyleSheet("color: green")
    
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
        img_gen.ai_generate(prompt_p, prompt_n, self.__current_model, self.__current_sampler, self.__current_steps)
        self.genFinished()
    
    def genFinished(self):
        self.gen_prog_icon.setPixmap(QPixmap("assets\\check.png").scaled(20,20))
        self.gen_prog_text.setText("Finished Generating Frames!")
      #  self.gen_prog_text.setStyleSheet("color: green")
    
    def stitchVideo(self):
        self.stitch_prog_icon.setVisible(True)
        self.stitch_prog_text.setVisible(True)
        animated_video_name = self.__file.split("/")[-1].split(".")[0]
        stitcher.stitch_frames(animated_video_name)
        self.stitchFinished()
    
    def stitchFinished(self):
        self.stitch_prog_icon.setPixmap(QPixmap("assets\\check.png").scaled(20,20))
        self.stitch_prog_text.setText("Finished Stitching Video!")
     #   self.stitch_prog_text.setStyleSheet("color: green")
    
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
        app.setStyleSheet(Path('./styles.qss').read_text())
        win = MyWindow()
        win.show()
        sys.exit(app.exec_())

window()
