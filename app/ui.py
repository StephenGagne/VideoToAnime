"""
This script implement PyQt5 GUI application for uploading
and displaying video using OpenCV
Author: Zachary and Vy 
Date: 2024-07-16
"""

'''
Current known issues:
- *Some* widget geometry is hard-coded, should be programmatically determined?
- Potential geometry issues on very small and very large displays
- Widgets outside of layout boxes are a headache to adjust geometry
'''
'''
Future Plans:
- Add preset style themes (light mode, dark mode?)
'''

import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout, QApplication, QMainWindow, QFileDialog, QProgressBar, QLabel, QTextEdit, QMessageBox, QDialog, QComboBox, QSpinBox, QPushButton, QFrame, QGroupBox, QDoubleSpinBox, QCheckBox, QRadioButton
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QMovie, QIcon
import cv2 as cv #import OpenCV library
import os
from importlib.metadata import version
import video_splitter
import ai_image_generation as img_gen
import frame_stitcher as stitcher
from cleanup import cleanup

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.move(100, 50)  #set size and position of window
        self.setWindowTitle("AnimateXpress")
        self.setWindowIcon(QIcon("assets/AnimateXpress.png"))
        self.setFixedSize(400, 860)  # Prevent resizing
        self.__file = None
        self.__frame_total = 0
        self.__recover_frame = 1
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

        #upload cosmetic line
        self.upload_line = QFrame(self)
        self.upload_line.setGeometry(20, 30, 360, 10)
        self.upload_line.setStyleSheet("color: rgba(56, 189, 248, 1);")
        self.upload_line.setFrameShape(QFrame.HLine)
        self.upload_line.setLineWidth(3)

        #upload button
        self.uploadButton = QPushButton(self)
        self.uploadButton.setText("Upload Video")
        self.uploadButton.move((int)(200 - (self.uploadButton.frameGeometry().width())/2), 20)
        self.uploadButton.clicked.connect(self.uploadClicked)
        self.uploadButton.setToolTip("Upload a video to be processed")

        #config 
        self.config_box = QGroupBox("Model Configuration", self)
        self.config_box.setGeometry(20, 70, 360, 375)
        self.config_layout = QGridLayout(self)
        self.config_layout.setOriginCorner(Qt.TopLeftCorner)
        self.config_layout.setVerticalSpacing(25)
        self.config_layout.setColumnStretch(0, 1)
        self.config_layout.setColumnStretch(1, 1)
        self.config_layout.setColumnStretch(2, 1)
        self.config_layout.setColumnStretch(3, 1)
  
        self.model_text = QLabel("Set Model:", self)
        self.model_text.setMinimumHeight(40)
        self.model_text.setMinimumWidth(180)
        self.sampler_text = QLabel("Set Sampler:", self)
        self.sampler_text.setMinimumHeight(40)
        self.sampler_text.setMinimumWidth(180)
        self.steps_text = QLabel("Select Number of Steps:", self)
        self.steps_text.setMinimumHeight(40)
        self.steps_text.setMinimumWidth(180)
        self.cfg_text = QLabel("Select CFG Value:", self)
        self.cfg_text.setMinimumHeight(40)
        self.cfg_text.setMinimumWidth(180)
        self.denoise_text = QLabel("Select Denoise Value:", self)
        self.denoise_text.setMinimumHeight(40)
        self.denoise_text.setMinimumWidth(180)
        self.descale_text = QLabel("Select Descale Value:", self)
        self.descale_text.setMinimumHeight(40)
        self.descale_text.setMinimumWidth(180)
  
        self.models = os.listdir("C:\AI_SD\webui\models\Stable-diffusion")
        for idx, model in enumerate(self.models):
            self.models[idx] = self.models[idx].split("/")[-1].rsplit(".")[0]
        self.samplers = ["Euler a", "Euler", "DPM++ 2M Karras", "DPM++ SDE Karras", "DPM++ 2M SDE Exponential", "DPM++ 2M SDE Karras", "LMS", "Heun", "DPM2", "DPM2 a", "DPM++ SDE", "DPM++ 2M SDE", "DPM++ 2M SDE Heun", "DPM++ 2M SDE Heun Karras", "DPM++ 2M SDE Heun Exponential", "DPM++ 3M SDE", "DPM++ 3M SDE Karras", "DPM++ 3M SDE Exponential", "DPM fast", "DPM adaptive", "LMS Karras", "DPM2 Karras", "DPM2 a Karras", "DPM++ 2S a Karras", "Restart", "DDIM", "PLMS", "UniPC", "LCM"]

        self.model_combo = QComboBox(self)
        self.model_combo.addItems(self.models)
        for i in range(0,len(self.models)-1):
            tooltip = self.model_combo.itemText(i)
            self.model_combo.setItemData(i, tooltip, QtCore.Qt.ToolTipRole)
        self.model_combo.setMinimumHeight(40)
        self.model_combo.setMinimumWidth(160)
        
        self.sampler_combo = QComboBox(self)
        self.sampler_combo.addItems(self.samplers)
        for i in range(0,len(self.samplers)-1):
            tooltip = self.sampler_combo.itemText(i)
            self.sampler_combo.setItemData(i, tooltip, QtCore.Qt.ToolTipRole)
        self.sampler_combo.setMinimumHeight(40)
        self.sampler_combo.setMinimumWidth(160)
        
        self.steps_spinner = QSpinBox(self)
        self.steps_spinner.setRange(10, 50)
        self.steps_spinner.setSingleStep(1)
        self.steps_spinner.setValue(15)
        self.steps_spinner.setMaximumWidth(50)
        self.steps_spinner.setMinimumHeight(40)
        self.steps_spinner.setAlignment(Qt.AlignCenter)
        self.steps_spinner.setToolTip("How many samples the sampler will take per frame.")
        
        self.cfg_spinner = QDoubleSpinBox(self)
        self.cfg_spinner.setRange(1, 20)
        self.cfg_spinner.setSingleStep(0.5)
        self.cfg_spinner.setValue(8)
        self.cfg_spinner.setMaximumWidth(50)
        self.cfg_spinner.setMinimumHeight(40)
        self.cfg_spinner.setAlignment(Qt.AlignCenter)
        self.cfg_spinner.setToolTip("How creative the AI is permitted to be.\nThe higher the value, the stricter the AI will be per the prompt text.\nFor best results use between 7 and 12.")
        
        self.denoise_spinner = QDoubleSpinBox(self)
        self.denoise_spinner.setRange(0, 1)
        self.denoise_spinner.setSingleStep(0.01)
        self.denoise_spinner.setValue(0.40)
        self.denoise_spinner.setMaximumWidth(50)
        self.denoise_spinner.setMinimumHeight(40)
        self.denoise_spinner.setAlignment(Qt.AlignCenter)
        self.denoise_spinner.setToolTip("How close each generated frame will be to the original frame.\nThe higher the value, the more details lost.\nFor best results, use a lower value.")
        
        self.descale_spinner = QDoubleSpinBox(self)
        self.descale_spinner.setRange(0, 1)
        self.descale_spinner.setSingleStep(0.05)
        self.descale_spinner.setValue(1)
        self.descale_spinner.setMaximumWidth(50)
        self.descale_spinner.setMinimumHeight(40)
        self.descale_spinner.setAlignment(Qt.AlignCenter)
        self.descale_spinner.setToolTip("The scale of the generated frames.")
        
        self.upscale_checkbox = QCheckBox("Upscale?", self)
        self.upscale_checkbox.setChecked(False)
        self.upscale_checkbox.stateChanged.connect(self.upscale_checked)
        self.upscale_checkbox.setMinimumHeight(40)
        
        self.upscale_model = QComboBox(self)
        self.upscale_model.addItems(self.models)
        for i in range(0,len(self.models)-1):
            tooltip = self.upscale_model.itemText(i)
            self.upscale_model.setItemData(i, tooltip, QtCore.Qt.ToolTipRole)
        self.upscale_model.setMinimumHeight(40)
        self.upscale_model.setMinimumWidth(160)
        self.upscale_model.setVisible(False)
        
        self.upscale_radio_group = QtWidgets.QButtonGroup(self)
        self.upscale_radio_720p = QRadioButton("720p")
        self.upscale_radio_1080p = QRadioButton("1080p")
        self.upscale_radio_4k = QRadioButton("4k")
        self.upscale_radio_8k = QRadioButton("8k")
        self.upscale_radio_group.addButton(self.upscale_radio_720p, 1280)
        self.upscale_radio_group.addButton(self.upscale_radio_1080p, 1920)
        self.upscale_radio_group.addButton(self.upscale_radio_4k, 3840)
        self.upscale_radio_group.addButton(self.upscale_radio_8k, 7680)
        self.upscale_radio_720p.setChecked(True)
        self.upscale_radio_720p.setVisible(False)
        self.upscale_radio_1080p.setVisible(False)
        self.upscale_radio_4k.setVisible(False)
        self.upscale_radio_8k.setVisible(False)
        
        self.config_layout.addWidget(self.model_text, 0, 0, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.model_combo, 0, 2, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.sampler_text, 1, 0, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.sampler_combo, 1, 2, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.steps_text, 2, 0, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.steps_spinner, 2, 2, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.cfg_text, 3, 0, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.cfg_spinner, 3, 2, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.denoise_text, 4, 0, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.denoise_spinner, 4, 2, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.descale_text, 5, 0, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.descale_spinner, 5, 2, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.upscale_checkbox, 6, 0, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.upscale_model, 6, 2, 2, 1, Qt.AlignTop)
        self.config_layout.addWidget(self.upscale_radio_720p, 7, 0, 1, 1, Qt.AlignCenter)
        self.config_layout.addWidget(self.upscale_radio_1080p, 7, 1, 1, 1, Qt.AlignCenter)
        self.config_layout.addWidget(self.upscale_radio_4k, 7, 2, 1, 1, Qt.AlignCenter)
        self.config_layout.addWidget(self.upscale_radio_8k, 7, 3, 1, 1, Qt.AlignCenter)  

        self.config_box.setLayout(self.config_layout)
        
        #prompts group
        self.prompt_box = QGroupBox("Prompt Configuration", self)
        self.prompt_box.setGeometry(20, 465, 360, 180)
        self.prompt_layout = QFormLayout(self)
        
        self.positive_prompt_text = QLabel("Positive Prompts: ", self)
        self.positive_prompt_text.setMinimumHeight(40)
        self.positive_prompt = QTextEdit(self)
        self.positive_prompt.setMinimumHeight(40)
        self.negative_prompt_text = QLabel("Negative Prompts:", self)
        self.negative_prompt_text.setMinimumHeight(40)
        self.negative_prompt = QTextEdit(self)
        self.negative_prompt.setMinimumHeight(40)
        
        self.prompt_layout.addRow(self.positive_prompt_text, self.positive_prompt)
        self.prompt_layout.addRow(self.negative_prompt_text, self.negative_prompt)
        self.prompt_box.setLayout(self.prompt_layout)

        #start cosmetic line
        self.start_line = QFrame(self)
        self.start_line.setGeometry(20, 670, 360, 10)
        self.start_line.setStyleSheet("color: rgba(56, 189, 248, 1);")
        self.start_line.setFrameShape(QFrame.HLine)
        self.start_line.setLineWidth(3)

        #start button
        self.startButton = QPushButton(self)
        self.startButton.setText("Generate Video")
        self.startButton.move((int)(200 - (self.startButton.frameGeometry().width())/2), 660)
        self.startButton.clicked.connect(self.startClicked)
        self.startButton.setEnabled(False)
        self.startButton.setToolTip("Initiate the conversion process")

        #split progress widgets
        self.split_prog_gif = QMovie("assets\\loading.gif")
        self.split_prog_loading = QLabel(self)
        self.split_prog_loading.setScaledContents(True)
        self.split_prog_loading.setGeometry(115, 705, 30, 30)
        self.split_prog_loading.setMaximumSize(30, 30)
        self.split_prog_loading.setMinimumSize(30, 30)
        self.split_prog_loading.setMovie(self.split_prog_gif)
        self.split_prog_loading.setVisible(False)
    
        self.split_prog_done = QLabel(self)
        self.split_prog_done.setGeometry(120, 710, 20, 20)
        self.split_prog_done.setPixmap(QPixmap("assets\\check.png").scaled(20,20))
        self.split_prog_done.setVisible(False)
        self.split_prog_text = QLabel(self)
        self.split_prog_text.setGeometry(160, 710, 200, 20)
        self.split_prog_text.setText("Splitting frames...")
        self.split_prog_text.setVisible(False)
        
        #imggen progress widgets
        self.gen_prog_gif = QMovie("assets\\loading.gif")
        self.gen_prog_loading = QLabel(self)
        self.gen_prog_loading.setScaledContents(True)
        self.gen_prog_loading.setGeometry(115, 760, 30, 30)
        self.gen_prog_loading.setMaximumSize(30, 30)
        self.gen_prog_loading.setMinimumSize(30, 30)
        self.gen_prog_loading.setMovie(self.gen_prog_gif)
        self.gen_prog_loading.setVisible(False)
        
        self.gen_prog_done = QLabel(self)
        self.gen_prog_done.setGeometry(120, 765, 20, 20)
        self.gen_prog_done.setPixmap(QPixmap("assets\\check.png").scaled(20,20))
        self.gen_prog_done.setVisible(False)
        self.gen_prog_text = QLabel(self)
        self.gen_prog_text.setGeometry(160, 765, 200, 20)
        self.gen_prog_text.setText("Generating frames...")
        self.gen_prog_text.setVisible(False)
        
        #stitch progress widgets
        self.stitch_prog_gif = QMovie("assets\\loading.gif")
        self.stitch_prog_loading = QLabel(self)
        self.stitch_prog_loading.setScaledContents(True)
        self.stitch_prog_loading.setGeometry(110, 815, 30, 30)
        self.stitch_prog_loading.setMaximumSize(30, 30)
        self.stitch_prog_loading.setMinimumSize(30, 30)
        self.stitch_prog_loading.setMovie(self.stitch_prog_gif)
        self.stitch_prog_loading.setVisible(False)
        
        self.stitch_prog_done = QLabel(self)
        self.stitch_prog_done.setGeometry(120, 820, 20, 20)
        self.stitch_prog_done.setPixmap(QPixmap("assets\\check.png").scaled(20,20))
        self.stitch_prog_done.setVisible(False)
        self.stitch_prog_text = QLabel(self)
        self.stitch_prog_text.setGeometry(160, 820, 200, 20)
        self.stitch_prog_text.setText("Stiching video back together...")
        self.stitch_prog_text.setVisible(False)
        
        if len(os.listdir("../generatedFrames")) > 1:
            self.recoverDetected()

    def upscale_checked(self):
        if self.upscale_checkbox.isChecked() == True:
            self.setFixedSize(400, 910)
            self.config_box.setGeometry(20, 70, 360, 425)
            self.prompt_box.setGeometry(20, 515, 360, 180)
            self.start_line.setGeometry(20, 720, 360, 10)
            self.startButton.move((int)(200 - (self.startButton.frameGeometry().width())/2), 710)
            self.split_prog_loading.setGeometry(115, 755, 30, 30)
            self.split_prog_done.setGeometry(120, 760, 20, 20)
            self.split_prog_text.setGeometry(160, 760, 200, 20)
            self.gen_prog_loading.setGeometry(115, 810, 30, 30)
            self.gen_prog_done.setGeometry(120, 815, 20, 20)
            self.gen_prog_text.setGeometry(160, 815, 200, 20)
            self.stitch_prog_loading.setGeometry(110, 865, 30, 30)
            self.stitch_prog_done.setGeometry(120, 870, 20, 20)
            self.stitch_prog_text.setGeometry(160, 870, 200, 20)
            self.upscale_model.setVisible(True)
            self.upscale_radio_720p.setVisible(True)
            self.upscale_radio_1080p.setVisible(True)
            self.upscale_radio_4k.setVisible(True)
            self.upscale_radio_8k.setVisible(True)
            
            print(self.upscale_radio_group.checkedId())
        else:
            self.setFixedSize(400, 860)
            self.config_box.setGeometry(20, 70, 360, 375)
            self.prompt_box.setGeometry(20, 465, 360, 180)
            self.start_line.setGeometry(20, 670, 360, 10)
            self.startButton.move((int)(200 - (self.startButton.frameGeometry().width())/2), 660)
            self.split_prog_loading.setGeometry(115, 705, 30, 30)
            self.split_prog_done.setGeometry(120, 710, 20, 20)
            self.split_prog_text.setGeometry(160, 710, 200, 20)
            self.gen_prog_loading.setGeometry(115, 760, 30, 30)
            self.gen_prog_done.setGeometry(120, 765, 20, 20)
            self.gen_prog_text.setGeometry(160, 765, 200, 20)
            self.stitch_prog_loading.setGeometry(110, 815, 30, 30)
            self.stitch_prog_done.setGeometry(120, 820, 20, 20)
            self.stitch_prog_text.setGeometry(160, 820, 200, 20)
            self.upscale_model.setVisible(False)
            self.upscale_radio_720p.setVisible(False)
            self.upscale_radio_1080p.setVisible(False)
            self.upscale_radio_4k.setVisible(False)
            self.upscale_radio_8k.setVisible(False)


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
      
    def startClicked(self):
        if self.positive_prompt.toPlainText() == "":
            errdlg1 = QMessageBox()
            errdlg1.setWindowTitle("Error - No Positive Prompts!")
            errdlg1.setIcon(QMessageBox.Critical)
            errdlg1.setText("Please add positive prompts before trying again!")
            errdlg1.exec_()
            return
        
        if self.model_combo.currentText() == "" or self.sampler_combo.currentText() == "":
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
        self.split_prog_loading.setVisible(True)
        self.split_prog_gif.start()
        self.split_prog_text.setVisible(True)
        video_splitter.split(self.__file)
        self.splitFinished()
        self.generateFrames()
        self.stitchVideo()
    
    def splitFinished(self):
        self.split_prog_gif.stop()
        self.split_prog_loading.setVisible(False)
        self.split_prog_done.setVisible(True)
        self.split_prog_text.setText("Finished Splitting Frames!")
        self.split_prog_text.setStyleSheet("color: green")
    
    def generateFrames(self):
        self.gen_prog_loading.setVisible(True)
        self.gen_prog_gif.start()
        self.gen_prog_text.setVisible(True)
        if self.positive_prompt.toPlainText() == "":
            prompt_p = ""
        else:
            prompt_p = self.positive_prompt.toPlainText()
        if self.negative_prompt.toPlainText() == "":
            prompt_n = ""
        else:
            prompt_n = self.negative_prompt.toPlainText() 
            
        modelName = self.model_combo.currentText()
        sampler = self.sampler_combo.currentText()
        steps = self.steps_spinner.value()
        cfg = self.cfg_spinner.value()
        denoise = self.denoise_spinner.value()
        descale = self.descale_spinner.value()
        upscale = self.upscale_checkbox.isChecked()
        upscale_loops = self.upscale_radio_group.checkedId() # Will return "2" for 2x, "3" for 3x, etc
        if(upscale):
            upscale_name = self.upscale_model.currentText()
            img_gen.generate_images(prompt_p, prompt_n, modelName, sampler, steps, cfg, denoise, descale, upscale, upscale_name, upscale_loops)
        else:
            img_gen.generate_images(prompt_p, prompt_n, modelName, sampler, steps, cfg, denoise, descale)
        self.genFinished()
    
    def genFinished(self):
        self.gen_prog_gif.stop()
        self.gen_prog_loading.setVisible(False)
        self.gen_prog_done.setVisible(True)
        self.gen_prog_text.setText("Finished Generating Frames!")
        self.gen_prog_text.setStyleSheet("color: green")
    
    def stitchVideo(self):
        self.stitch_prog_loading.setVisible(True)
        self.stitch_prog_gif.start()
        self.stitch_prog_text.setVisible(True)
        animated_video_name = self.__file.split("/")[-1].split(".")[0]
        stitcher.stitch_frames(animated_video_name, self.__file)
        self.stitchFinished()
    
    def stitchFinished(self):
        self.stitch_prog_gif.stop()
        self.stitch_prog_loading.setVisible(False)
        self.stitch_prog_done.setVisible(True)
        self.stitch_prog_text.setText("Finished Stitching Video!")
        self.stitch_prog_text.setStyleSheet("color: green")
        cleanup()
            
    def recoverDetected(self):
        self.uploadButton.setVisible(False)
        self.upload_line.setVisible(False)
        self.config_box.setVisible(False)
        self.prompt_box.setVisible(False)
        self.startButton.setVisible(False)
        self.start_line.setVisible(False)
        
        self.recover_label_1 = QLabel("An unfinished project was detected.", self)
        self.recover_label_1.setGeometry(20, 300, 360, 25)
        self.recover_label_1.setAlignment(Qt.AlignCenter)
        self.recover_label_1.setStyleSheet("color: red;")
        
        self.recover_label_2 = QLabel("Do you want to recover progress?", self)
        self.recover_label_2.setGeometry(20, 330, 360, 25)
        self.recover_label_2.setAlignment(Qt.AlignCenter)
        self.recover_label_2.setStyleSheet("font-weight: bold;")

        self.recover_yes = QPushButton(self)
        self.recover_yes.setText("Yes, Recover Project")
        self.recover_yes.setGeometry(20, 370, 175, 50)
        self.recover_yes.clicked.connect(self.recoverProject)
    
        self.recover_no = QPushButton(self)
        self.recover_no.setText("No, Overwrite Project")
        self.recover_no.setGeometry(205, 370, 175, 50)
        self.recover_no.clicked.connect(self.confirmOverwrite)
        
        self.recover_thumbnail = QLabel(self)
        self.recover_thumbnail.setGeometry(104, 460, 200, 200)
        self.recover_thumbnail.setAlignment(Qt.AlignCenter)
        self.recover_thumbnail.setPixmap(QPixmap("../generatedFrames/frame0.png").scaled(208,117))
        
    
    def recoverProject(self):
        recovered_frames = os.listdir("../generatedFrames")
        self.__recover_frame = len(recovered_frames) # subtract README
        print(self.__recover_frame)
        
        self.recover_label_1.setVisible(False)
        self.recover_label_2.setVisible(False)
        self.recover_yes.setVisible(False)
        self.recover_no.setVisible(False)
        self.recover_thumbnail.setVisible(False)
        
        self.uploadButton.setVisible(True)
        self.upload_line.setVisible(True)
        self.config_box.setVisible(True)
        self.prompt_box.setVisible(True)
        self.startButton.setVisible(True)
        self.start_line.setVisible(True)
    
    def confirmOverwrite(self):
        self.recover_label_1.setText("This will permanently delete the previous project.")
        self.recover_label_2.setText("Would you like to continue?")
        
        self.recover_yes.setText("Yes, Overwrite Project")
        self.recover_yes.setStyleSheet("background-color: red; color: white")
        self.recover_yes.clicked.connect(self.overwriteProject)
        
        self.recover_no.setText("No")
        self.recover_no.clicked.connect(self.initUI)
        
    def overwriteProject(self):
        cleanup()
        os.execl(sys.executable, *sys.orig_argv)
            
    
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
        app.setStyleSheet(Path('../config/styles.qss').read_text())
        win = MyWindow()
        win.show()
        sys.exit(app.exec_())

window()
