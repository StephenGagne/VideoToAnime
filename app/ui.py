# System Imports
import sys
import os
from pathlib import Path
from urllib.request import urlopen
from urllib.error import *
# Dependency Imports
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QObject, QThread, QSettings
from PyQt5.QtGui import QPixmap, QMovie, QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout, QApplication, QMainWindow, QFileDialog, QLabel, QTextEdit, QMessageBox, QComboBox, QSpinBox, QPushButton, QFrame, QGroupBox, QDoubleSpinBox, QCheckBox, QRadioButton
import cv2 as cv
# Custom Imports
import video_splitter
import ai_image_generation as img_gen
import frame_stitcher as stitcher
from cleanup import cleanup
from directory import *

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.move(100, 50)  #set size and position of window
        self.setWindowTitle("AnimateXpress")
        self.setWindowIcon(QIcon("assets/AnimateXpress.png"))
        self.setFixedSize(400, 910)  # Prevent resizing
        self.settings = QSettings("../config/settings.ini", QSettings.IniFormat)
        self.__file = None
        self.__frame_total = 0
        self.__recover_frame = 1
        self.initUI()

##
# - UI Initialisation Function -
# Establishes the widget framework
# and connects the signals and slots
# used to link components
# to their respective functions
##
    def initUI(self): 
        mainWindow = QWidget()
        self.setCentralWidget(mainWindow)
        
        VLayout = QVBoxLayout()
        mainWindow.setLayout(VLayout)
        HLayout = QHBoxLayout()
        mainWindow.setLayout(HLayout)

        ##
        # - Upload Button Components -
        # Contains the cosmetic line passing through
        # the upload button, the button itself, and
        # the upload button text label.
        ##
        self.upload_line = QFrame(self)
        self.upload_line.setGeometry(20, 30, 360, 10)
        self.upload_line.setStyleSheet("color: rgba(56, 189, 248, 1);")
        self.upload_line.setFrameShape(QFrame.HLine)
        self.upload_line.setLineWidth(3)

        self.uploadButton = QPushButton(self)
        self.uploadButton.setText("Upload Video")
        self.uploadButton.move((int)(200 - (self.uploadButton.frameGeometry().width())/2), 20)
        self.uploadButton.clicked.connect(self.uploadClicked)
        self.uploadButton.setToolTip("Upload a video to be processed")

        ##
        # - Configuration Box and Contained Widgets - 
        # Contains the box framework, configuration widgets
        # (model, sampler, and upscale model dropdowns, 
        # steps, cfg, denoise, and descale spinners,
        # upscale checkbox and radio buttons) and their 
        # corresponding text labels.
        ##
        self.config_box = QGroupBox("Model Configuration", self)
        self.config_layout = QGridLayout(self)
        self.config_layout.setOriginCorner(Qt.TopLeftCorner)
  
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
  
        self.models = os.listdir("..\config\Models")#(SDDIR)#("C:\AI_SD\webui\models\Stable-diffusion")
        for idx, model in enumerate(self.models):
            self.models[idx] = self.models[idx].split("/")[-1].rsplit(".")[0]
        self.samplers = ["Euler a", "Euler", "DPM++ 2M Karras", "DPM++ SDE Karras", "DPM++ 2M SDE Exponential", "DPM++ 2M SDE Karras", "LMS", "Heun", "DPM2", "DPM2 a", "DPM++ SDE", "DPM++ 2M SDE", "DPM++ 2M SDE Heun", "DPM++ 2M SDE Heun Karras", "DPM++ 2M SDE Heun Exponential", "DPM++ 3M SDE", "DPM++ 3M SDE Karras", "DPM++ 3M SDE Exponential", "DPM fast", "DPM adaptive", "LMS Karras", "DPM2 Karras", "DPM2 a Karras", "DPM++ 2S a Karras", "Restart", "DDIM", "PLMS", "UniPC", "LCM"]
        
        self.model_combo = QComboBox(self)
        self.model_combo.addItems(self.models)
        for i in range(0,len(self.models)-1):
            tooltip = self.model_combo.itemText(i)
            self.model_combo.setItemData(i, tooltip, QtCore.Qt.ToolTipRole)
        if self.settings.contains("model"):
            if self.settings.value("model") in self.models:                 
                self.model_combo.setCurrentIndex(self.models.index(self.settings.value("model")))
        self.model_combo.setMinimumHeight(40)
        self.model_combo.setMinimumWidth(160)
        self.model_combo.setToolTip("Select the model used for the image generation.")
        
        self.sampler_combo = QComboBox(self)
        self.sampler_combo.addItems(self.samplers)
        for i in range(0,len(self.samplers)-1):
            tooltip = self.sampler_combo.itemText(i)
            self.sampler_combo.setItemData(i, tooltip, QtCore.Qt.ToolTipRole)
        if self.settings.contains("sampler"):
            self.sampler_combo.setCurrentIndex(self.samplers.index(self.settings.value("sampler")))
        self.sampler_combo.setMinimumHeight(40)
        self.sampler_combo.setMinimumWidth(160)
        self.sampler_combo.setToolTip("Select the sampler used for the image generation.")
        
        self.steps_spinner = QSpinBox(self)
        self.steps_spinner.setRange(10, 50)
        self.steps_spinner.setSingleStep(1)
        if self.settings.contains("steps"):
            self.steps_spinner.setValue(int(self.settings.value("steps")))
        else:
            self.steps_spinner.setValue(15)
        self.steps_spinner.setMaximumWidth(50)
        self.steps_spinner.setMinimumHeight(40)
        self.steps_spinner.setAlignment(Qt.AlignCenter)
        self.steps_spinner.setToolTip("How many samples the sampler will take per frame.")
        
        self.cfg_spinner = QDoubleSpinBox(self)
        self.cfg_spinner.setRange(1, 20)
        self.cfg_spinner.setSingleStep(0.5)
        if self.settings.contains("cfg"):
            self.cfg_spinner.setValue(float(self.settings.value("cfg")))
        else:
            self.cfg_spinner.setValue(8)
        self.cfg_spinner.setMaximumWidth(50)
        self.cfg_spinner.setMinimumHeight(40)
        self.cfg_spinner.setAlignment(Qt.AlignCenter)
        self.cfg_spinner.setToolTip("How creative the AI is permitted to be.\nThe higher the value, the stricter the AI will be per the prompt text.\nFor best results use between 7 and 12.")
        
        self.denoise_spinner = QDoubleSpinBox(self)
        self.denoise_spinner.setRange(0, 1)
        self.denoise_spinner.setSingleStep(0.01)
        if self.settings.contains("denoise"):
            self.denoise_spinner.setValue(float(self.settings.value("denoise")))
        else:
            self.denoise_spinner.setValue(0.40)
        self.denoise_spinner.setMaximumWidth(50)
        self.denoise_spinner.setMinimumHeight(40)
        self.denoise_spinner.setAlignment(Qt.AlignCenter)
        self.denoise_spinner.setToolTip("How close each generated frame will be to the original frame.\nThe higher the value, the more details lost.\nFor best results, use a lower value.")
        
        self.descale_spinner = QDoubleSpinBox(self)
        self.descale_spinner.setRange(0, 1)
        self.descale_spinner.setSingleStep(0.05)
        if self.settings.contains("descale"):
            self.descale_spinner.setValue(float(self.settings.value("descale")))
        else:
            self.descale_spinner.setValue(1)
        self.descale_spinner.setMaximumWidth(50)
        self.descale_spinner.setMinimumHeight(40)
        self.descale_spinner.setAlignment(Qt.AlignCenter)
        self.descale_spinner.setToolTip("The scale of the generated frames.")
        
        self.upscale_checkbox = QCheckBox("Upscale?", self)
        if self.settings.contains("upscale_checked"):
            if self.settings.value("upscale_checked") == "true":
                self.upscale_checkbox.setChecked(True)
            if self.settings.value("upscale_checked") == "false":
                self.upscale_checkbox.setChecked(False)
        self.upscale_checkbox.stateChanged.connect(self.upscale_checked)
        self.upscale_checkbox.setMinimumHeight(40)
        self.upscale_checkbox.setToolTip("Check to enable upscaling functionality and show upscale options.")
        
        self.upscale_model = QComboBox(self)
        self.upscale_model.addItems(self.models)
        for i in range(0,len(self.models)-1):
            tooltip = self.upscale_model.itemText(i)
            self.upscale_model.setItemData(i, tooltip, QtCore.Qt.ToolTipRole)
        if self.settings.contains("upscale_model"):
            if self.settings.value("upscale_model") in self.models:                 
                self.upscale_model.setCurrentIndex(self.models.index(self.settings.value("upscale_model")))
        self.upscale_model.setMinimumHeight(40)
        self.upscale_model.setMinimumWidth(160)
        self.upscale_model.setVisible(False)
        self.upscale_model.setToolTip("Select which model used for the upscaling.")
        
        self.upscale_radio_group = QtWidgets.QButtonGroup(self)
        self.upscale_radio_720p = QRadioButton("720p")
        self.upscale_radio_1080p = QRadioButton("1080p")
        self.upscale_radio_4k = QRadioButton("4K")
        self.upscale_radio_8k = QRadioButton("8K")
        self.upscale_radio_group.addButton(self.upscale_radio_720p, 1260)
        self.upscale_radio_group.addButton(self.upscale_radio_1080p, 1920)
        self.upscale_radio_group.addButton(self.upscale_radio_4k, 3840)
        self.upscale_radio_group.addButton(self.upscale_radio_8k, 7680)
        self.upscale_radio_720p.setVisible(False)
        self.upscale_radio_1080p.setVisible(False)
        self.upscale_radio_4k.setVisible(False)
        self.upscale_radio_8k.setVisible(False)
        self.upscale_warning = QLabel("Using upscaling will drastically increase rendering time!")
        self.upscale_warning.setStyleSheet("color: red; border-color: white;")
        self.upscale_warning.setVisible(False)
        self.upscale_warning.setMaximumHeight(25)
        self.upscale_warning.setMinimumWidth(340)
        
        if self.settings.contains("upscale_resolution"):
            if int(self.settings.value("upscale_resolution")) == 1280:
                self.upscale_radio_720p.setChecked(True)
            elif int(self.settings.value("upscale_resolution")) == 1920:
                self.upscale_radio_1080p.setChecked(True)
            elif int(self.settings.value("upscale_resolution")) == 3840:
                self.upscale_radio_4k.setChecked(True)
            elif int(self.settings.value("upscale_resolution")) == 7680:
                self.upscale_radio_8k.setChecked(True)
            else:
                self.upscale_radio_720p.setChecked(True)    
        else:
            self.upscale_radio_720p.setChecked(True)                
        
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
        self.config_layout.addWidget(self.upscale_radio_8k, 7, 3, 1, 1, Qt.AlignLeft)  
        self.config_layout.addWidget(self.upscale_warning, 8, 0, -1, 1, Qt.AlignCenter)
        
        self.config_layout.setVerticalSpacing(25)
        self.config_layout.setColumnStretch(0, 1)
        self.config_layout.setColumnStretch(1, 1)
        self.config_layout.setColumnStretch(2, 1)
        self.config_layout.setColumnStretch(3, 1)
        self.config_layout.setRowStretch(0, 3)
        self.config_layout.setRowStretch(1, 3)
        self.config_layout.setRowStretch(2, 3)
        self.config_layout.setRowStretch(3, 3)
        self.config_layout.setRowStretch(4, 3)
        self.config_layout.setRowStretch(5, 3)
        self.config_layout.setRowStretch(6, 3)
        self.config_layout.setRowStretch(7, 3)
        self.config_layout.setRowStretch(8, 0)

        self.config_box.setGeometry(20, 70, 360, 375)
        self.config_box.setLayout(self.config_layout)
        
        ##
        # - Prompt Input Box and Text Inputs - 
        # Contains the prompt box framerwork, the
        # positive and negative text input boxes,
        # and the corresponding text labels.
        ##
        self.prompt_box = QGroupBox("Prompt Configuration", self)
        self.prompt_box.setGeometry(20, 465, 360, 180)
        self.prompt_layout = QFormLayout(self)
        
        self.positive_prompt_text = QLabel("Positive Prompts: ", self)
        self.positive_prompt_text.setMinimumHeight(40)
        self.positive_prompt = QTextEdit(self)
        if self.settings.contains("positive_prompt"):
            self.positive_prompt.setText(self.settings.value("positive_prompt"))
        self.positive_prompt.setMinimumHeight(40)
        self.negative_prompt_text = QLabel("Negative Prompts:", self)
        self.negative_prompt_text.setMinimumHeight(40)
        self.negative_prompt = QTextEdit(self)
        if self.settings.contains("negative_prompt"):
            self.negative_prompt.setText(self.settings.value("negative_prompt"))
        self.negative_prompt.setMinimumHeight(40)
        
        self.prompt_layout.addRow(self.positive_prompt_text, self.positive_prompt)
        self.prompt_layout.addRow(self.negative_prompt_text, self.negative_prompt)
        self.prompt_box.setLayout(self.prompt_layout)

        ##
        # - Start Button Components -
        # Contains the cosmetic line passing through
        # the upload button, the start button itself,
        # the cancel button that replaces the start
        # button during generation, and their corresponding
        # text labels.
        ##
        self.start_line = QFrame(self)
        self.start_line.setGeometry(20, 670, 360, 10)
        self.start_line.setStyleSheet("color: rgba(56, 189, 248, 1);")
        self.start_line.setFrameShape(QFrame.HLine)
        self.start_line.setLineWidth(3)

        self.startButton = QPushButton(self)
        self.startButton.setText("Generate Video")
        self.startButton.move((int)(200 - (self.startButton.frameGeometry().width())/2), 660)
        self.startButton.clicked.connect(self.startClicked)
        self.startButton.setEnabled(False)
        self.startButton.setToolTip("Initiate the conversion process")
        
        self.cancelButton = QPushButton(self)
        self.cancelButton.setText("Cancel")
        self.cancelButton.move((int)(200 - (self.cancelButton.frameGeometry().width())/2), 660)
        self.cancelButton.clicked.connect(self.cancelClicked)
        self.cancelButton.setEnabled(False)
        self.cancelButton.setVisible(False)
        self.cancelButton.setToolTip("Cancel the conversion process")

        ##
        # - Generation Progress Widgets and Assets - 
        # Contains the widgets responsible for displaying
        # the progress of image generation, split between
        # the video splitting (split_), the image generation (gen_),
        # and the video re-stitching (stitch_). Each group contains 
        # a loading gif (_prog_gif), a completed png (_prog_done),
        # a text label (_prog_text), a label that contains 
        # the gif (_prog_loading_)
        # 
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
        self.stitch_prog_text.setText("Stiching the video back together...")
        self.stitch_prog_text.setVisible(False)
        
        ## 
        # - Final checks for warnings and prior configurations -
        ##
        if len(os.listdir("../generatedFrames")) > 1:
            self.recoverDetected()
        
        if self.upscale_checkbox.isChecked() is True:
            self.upscale_checked()
        
        self.auto1111check()

    ##
    # - Check for Stable Diffusion Automatic 1111 -
    # Checks if the user has properly installed and run
    # the Stable Diffusion Automatic 1111 api required
    # to generate. If the user has not, then a warning
    # prompt is displayed prior to the GUI being shown
    # for the first time.
    ##
    def auto1111check(self):
        try:
            html = urlopen("http://127.0.0.1:7860/sdapi/v1/img2img")
        except HTTPError as e:
            if(e.code == 404):
                a1111dlg = QMessageBox()
                a1111dlg.setWindowTitle("Error - Automatic 1111 Not Found!")
                a1111dlg.setIcon(QMessageBox.Critical)
                a1111dlg.setText("Automatic 1111 is either not running or not running in api mode.\nIf not running go to your automatic1111 root directory and run run.bat\nIf it is running then please add --api to COMMANDLINE-ARGS in automatic1111/webui/webui-user.bat and run it again")
                a1111dlg.exec_()
        except URLError:
            a1111dlg = QMessageBox()
            a1111dlg.setWindowTitle("Error - Automatic 1111 Not Found!")
            a1111dlg.setIcon(QMessageBox.Critical)
            a1111dlg.setText("Automatic 1111 is either not running or not running in api mode.\nIf not running go to your automatic1111 root directory and run run.bat\nIf it is running then please add --api to COMMANDLINE-ARGS in automatic1111/webui/webui-user.bat and run it again")
            a1111dlg.exec_()
    
    ##
    # - Helper Function for Upscale Widgets -
    # Adjusts the GUI to account for the upscaling
    # configuration options that are hidden or
    # shown based on the upscale checkbox state.
    ##
    def upscale_checked(self):
        if self.upscale_checkbox.isChecked() == True:
            self.setFixedSize(400, 950)
            self.move(100, 25)
            self.config_box.setGeometry(20, 70, 360, 475)
            self.prompt_box.setGeometry(20, 565, 360, 180)
            self.start_line.setGeometry(20, 770, 360, 10)
            self.startButton.move((int)(200 - (self.startButton.frameGeometry().width())/2), 760)
            self.cancelButton.move((int)(200 - (self.startButton.frameGeometry().width())/2), 760)
            self.split_prog_loading.setGeometry(115, 805, 30, 30)
            self.split_prog_done.setGeometry(120, 810, 20, 20)
            self.split_prog_text.setGeometry(160, 810, 200, 20)
            self.gen_prog_loading.setGeometry(115, 860, 30, 30)
            self.gen_prog_done.setGeometry(120, 865, 20, 20)
            self.gen_prog_text.setGeometry(160, 865, 200, 20)
            self.stitch_prog_loading.setGeometry(110, 915, 30, 30)
            self.stitch_prog_done.setGeometry(120, 920, 20, 20)
            self.stitch_prog_text.setGeometry(160, 920, 200, 20)
            self.upscale_model.setVisible(True)
            self.upscale_radio_720p.setVisible(True)
            self.upscale_radio_1080p.setVisible(True)
            self.upscale_radio_4k.setVisible(True)
            self.upscale_radio_8k.setVisible(True)
            self.upscale_warning.setVisible(True)
            
        else:
            self.setFixedSize(400, 860)
            self.move(100, 50)
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
            self.upscale_warning.setVisible(False)


    ##
    # - Functionality for Upload Button -
    # Facilitates the upload button's signal
    # and allows the user to select a file from
    # their directory. Will flag if the file is 
    # not the correct file type (.mp4, .avi, or .mov).
    ##
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
      
    ##
    # - Functionality for Start Button -
    # Handles the start button's signal and
    # begins the process. Will flag if there are 
    # unfilled required configuration options (file,
    # model, sampler, positive prompts). This function
    # also handles saving the current settings to 
    # the persistence .ini file to be reloaded
    # on the next open.
    ##
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
            self.startButton.setVisible(False)
            self.startButton.setEnabled(False)
            self.cancelButton.setVisible(True)
            self.cancelButton.setEnabled(True)
            
            self.settings.setValue("positive_prompt", self.positive_prompt.toPlainText())
            self.settings.setValue("negative_prompt", self.negative_prompt.toPlainText())    
            self.settings.setValue("model", self.model_combo.currentText())
            self.settings.setValue("sampler", self.sampler_combo.currentText())
            self.settings.setValue("steps", self.steps_spinner.value())
            self.settings.setValue("cfg", self.cfg_spinner.value())
            self.settings.setValue("denoise", self.denoise_spinner.value())
            self.settings.setValue("descale", self.descale_spinner.value())
            self.settings.setValue("upscale_checked", self.upscale_checkbox.isChecked())
            self.settings.setValue("upscale_model", self.upscale_model.currentText())
            self.settings.setValue("upscale_resolution", self.upscale_radio_group.checkedId())
            self.settings.sync()
            
    ##
    # - Helper Function for Cancel - 
    # Handles the signal for the cancel button.
    # Restarts the program when clicked.
    ##   
    def cancelClicked(self):
        os.execl(sys.executable, *sys.orig_argv) 
    
    ##
    # - Functionality for Frame Splitting -
    # Calls the frame splitting script and
    # adjusts the related progress labels/assets.
    ##             
    def splitFrames(self):
        self.split_prog_loading.setVisible(True)
        self.split_prog_gif.start()
        self.split_prog_text.setVisible(True)
        video_splitter.split(self.__file)
        self.splitFinished()
        self.generateFrames()
        self.stitchVideo()
    
    ##
    # - Splitting Finished Emit - 
    # Signifies that the video has finished splitting
    # and updates the related progress labels/assets.
    ##
    def splitFinished(self):
        self.split_prog_gif.stop()
        self.split_prog_loading.setVisible(False)
        self.split_prog_done.setVisible(True)
        self.split_prog_text.setText("Finished Splitting Frames!")
        self.split_prog_text.setStyleSheet("color: green")
    ##
    # - Functionality for Frame Generation - 
    # Calls the image generation script with
    # the user's defined configuration and
    # updates the related progress labels/assets.
    ##
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
    ##
    # - Generation Finished Emit -
    # Signals that the image generation 
    # has completed successfully and adjusts
    # the related labels/assets.
    ##
    def genFinished(self):
        self.gen_prog_gif.stop()
        self.gen_prog_loading.setVisible(False)
        self.gen_prog_done.setVisible(True)
        self.gen_prog_text.setText("Finished Generating Frames!")
        self.gen_prog_text.setStyleSheet("color: green")
    ##
    # - Functionality for Video Stitching - 
    # Calls the video stitching script with
    # the user's defined configuration and
    # updates the related progress labels/assets.
    ##
    def stitchVideo(self):
        self.stitch_prog_loading.setVisible(True)
        self.stitch_prog_gif.start()
        self.stitch_prog_text.setVisible(True)
        animated_video_name = self.__file.split("/")[-1].split(".")[0]
        stitcher.stitch_frames(animated_video_name, self.__file)
        self.stitchFinished()
    ##
    # - Stitching Finished Emit -
    # Signals that the video stitching 
    # has completed successfully and adjusts
    # the related labels/assets. This function
    # will also call the cleanup script to
    # clean the directories of any files used
    # within the image generation process that
    # are no longer needed.
    ##
    def stitchFinished(self):
        self.stitch_prog_gif.stop()
        self.stitch_prog_loading.setVisible(False)
        self.stitch_prog_done.setVisible(True)
        self.stitch_prog_text.setText("Finished Stitching Video!")
        self.stitch_prog_text.setStyleSheet("color: green")
        cleanup()
    
    ##
    # - Recover Detection Function -
    # Hides the default GUI widgets and displays
    # a set of buttons and labels indicating
    # that there were files found leftover in
    # the directories (signifying the previous
    # runtime was interrupted or failed) and allows
    # the user to overwrite or recover. This function
    # will also display a thumbnail of the first frame
    # in the found files to serve as a reminder of 
    # the previous generation attempt.
    ##        
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
        
    ##
    # - Helper Function for Recovery - 
    # Handles the button signals for 
    # when a recovery is selected instead
    # of an overwrite and returns the GUI
    # to its default state.
    ##
    def recoverProject(self):
        recovered_frames = os.listdir("../generatedFrames")
        self.__recover_frame = len(recovered_frames)
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
    
    ## 
    # - Overwrite Confirmation - 
    # Handles the secondary overwrite screen
    # that prompts the user to confirm before
    # deleting the found files.
    ##
    def confirmOverwrite(self):
        self.recover_label_1.setText("This will permanently delete the previous project.")
        self.recover_label_2.setText("Would you like to continue?")
        
        self.recover_yes.setText("Yes, Overwrite Project")
        self.recover_yes.setStyleSheet("background-color: red; color: white")
        self.recover_yes.clicked.connect(self.overwriteProject)
        
        self.recover_no.setText("No")
        self.recover_no.clicked.connect(self.initUI)
    
    ##
    # - Helper Function for Overwriting - 
    # Handles the signal from the overwrite confirm
    # button and cleans the directory before
    # restarting the program.
    ##    
    def overwriteProject(self):
        cleanup()
        os.execl(sys.executable, *sys.orig_argv)
            
##
# - Worker Object -
# Worker class to handle multithreading
# functionality.
##    
class Worker(QObject):
    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        self.function(*self.args, **self.kwargs)

##
# - Background Window Function - 
# Initiates the program's backbone.
# Serves as a "main()" function.
##        
def window():
        app = QApplication(sys.argv)
        app.setStyleSheet(Path('../config/styles.qss').read_text())
        win = MyWindow()
        win.show()
        sys.exit(app.exec_())

window()
