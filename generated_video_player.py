import sys
import cv2
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QComboBox)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class GeneratedVideoPlayer(QWidget):
    def __init__(self, video_file_path, csv_path):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.player1 = SingleVideoPlayer(self, video_file_path)
        self.layout.addWidget(self.player1)
        
        self.selectChartTypeLayout = QHBoxLayout()
        
        self.selectChartTypeLayout.addStretch(1)
        
        self.SelectChartTypeLabel = QLabel("Chart Type", self)
        self.selectChartTypeLayout.addWidget(self.SelectChartTypeLabel)

        self.comboBox = QComboBox(self)
        self.comboBox.addItem("positionX")
        self.comboBox.addItem("positionY")
        self.comboBox.addItem("angle")
        self.selectChartTypeLayout.addWidget(self.comboBox)


        self.layout.addLayout(self.selectChartTypeLayout)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.data = pd.read_csv(csv_path)
        self.base_data = self.data.filter(regex=" Base$")
        self.overlap_data = self.data.filter(regex=" Overlap$")
        
        self.pointComboBoxLayout = QHBoxLayout()
        self.pointComboBoxLayout.addStretch(1)
        self.pointAComboBoxLabel = QLabel("pointA", self)
        self.pointComboBoxLayout.addWidget(self.pointAComboBoxLabel)
        self.pointAComboBox = QComboBox(self)
        self.pointComboBoxLayout.addWidget(self.pointAComboBox)
        
        self.pointBComboBoxLabel = QLabel("pointB", self)
        self.pointComboBoxLayout.addWidget(self.pointBComboBoxLabel)
        self.pointBComboBox = QComboBox(self)
        self.pointComboBoxLayout.addWidget(self.pointBComboBox)
        
        self.pointCComboBoxLabel = QLabel("pointC", self)
        self.pointComboBoxLayout.addWidget(self.pointCComboBoxLabel)
        self.pointCComboBox = QComboBox(self)
        self.pointComboBoxLayout.addWidget(self.pointCComboBox)

        body_parts = list(dict.fromkeys([col.split(' ')[0][:-1] for col in self.base_data.columns]))
        body_parts.extend(['waistCenter', 'shoulderCenter'])

        self.pointAComboBox.addItems(body_parts)
        self.pointBComboBox.addItems(body_parts)
        self.pointCComboBox.addItems(body_parts + ['horizontal'])

        self.layout.addLayout(self.pointComboBoxLayout)

        self.comboBox.currentIndexChanged.connect(self.update_graph)
        self.pointAComboBox.currentIndexChanged.connect(self.update_graph)
        self.pointBComboBox.currentIndexChanged.connect(self.update_graph)
        self.pointCComboBox.currentIndexChanged.connect(self.update_graph)
        self.player1.slider.valueChanged.connect(self.update_graph)
        
        self.comboBox.currentIndexChanged.connect(self.update_ui)

        self.setLayout(self.layout)
        self.setWindowTitle("Movement Comparison Video Generator")
        self.resize(1600, 900)

        self.update_graph()
        self.update_ui()

    def calculate_angle_between_three_points(self, pointA, pointB, pointC):
        vectorAB = pointB - pointA
        vectorBC = pointC - pointB
        
        dot_product = np.sum(vectorAB * vectorBC, axis=1)
        norm_ab = np.linalg.norm(vectorAB, axis=1)
        norm_bc = np.linalg.norm(vectorBC, axis=1)
        
        angles_rad = np.arccos(dot_product / (norm_ab * norm_bc))
        angles_deg = np.degrees(angles_rad)
        
        return 180 - angles_deg #時計回りになるように180度引く

    def update_graph(self):
        self.ax.clear()
        if self.comboBox.currentText() == "positionX":
            part_name = self.pointAComboBox.currentText()
            
            if part_name == "waistCenter" or part_name == "shoulderCenter":
                self.calculate_center_point(self.base_data, self.overlap_data, part_name)

            base_dataX = self.base_data[f"{part_name}X Base"].values
            overlap_dataX = self.overlap_data[f"{part_name}X Overlap"].values
            
            self.ax.plot(base_dataX, label="Base")
            self.ax.plot(overlap_dataX, label="Overlap")
        elif self.comboBox.currentText() == "positionY":
            part_name = self.pointAComboBox.currentText()
            
            if part_name == "waistCenter" or part_name == "shoulderCenter":
                self.calculate_center_point(self.base_data, self.overlap_data, part_name)
            
            base_dataY = self.base_data[f"{part_name}Y Base"].values
            overlap_dataY = self.overlap_data[f"{part_name}Y Overlap"].values
            
            self.ax.plot(base_dataY, label="Base")
            self.ax.plot(overlap_dataY, label="Overlap")
        elif self.comboBox.currentText() == "angle":
            pointA_name = self.pointAComboBox.currentText()
            pointB_name = self.pointBComboBox.currentText()
            pointC_name = self.pointCComboBox.currentText()
            
            if pointA_name == "waistCenter" or pointA_name == "shoulderCenter":
                self.calculate_center_point(self.base_data, self.overlap_data, pointA_name)
                
            if pointB_name == "waistCenter" or pointB_name == "shoulderCenter":
                self.calculate_center_point(self.base_data, self.overlap_data, pointB_name)
            if pointC_name == "waistCenter" or pointC_name == "shoulderCenter":
                self.calculate_center_point(self.base_data, self.overlap_data, pointC_name)
            
            pointA_base = self.base_data[[f"{pointA_name}X Base", f"{pointA_name}Y Base"]].values
            pointB_base = self.base_data[[f"{pointB_name}X Base", f"{pointB_name}Y Base"]].values
            pointA_overlap = self.overlap_data[[f"{pointA_name}X Overlap", f"{pointA_name}Y Overlap"]].values
            pointB_overlap = self.overlap_data[[f"{pointB_name}X Overlap", f"{pointB_name}Y Overlap"]].values
            
            if pointC_name == "horizontal":
                pointC_base = np.copy(pointB_base)
                pointC_base[:, 0] = 0  # Y座標を0にして水平線を表現
                pointC_overlap = np.copy(pointB_overlap)
                pointC_overlap[:, 0] = 0  # Y座標を0にして水平線を表現
            else:
                pointC_base = self.base_data[[f"{pointC_name}X Base", f"{pointC_name}Y Base"]].values
                pointC_overlap = self.overlap_data[[f"{pointC_name}X Overlap", f"{pointC_name}Y Overlap"]].values
            
            angles_base = self.calculate_angle_between_three_points(pointA_base, pointB_base, pointC_base)
            self.ax.plot(angles_base, label="Base")
            angles_overlap = self.calculate_angle_between_three_points(pointA_overlap, pointB_overlap, pointC_overlap)
            self.ax.plot(angles_overlap, label="Overlap")

        self.ax.axvline(x=self.player1.get_current_frame() - 1, color='r', linestyle='--')
        self.ax.legend()
        self.ax.set_xlim([0, self.player1.get_total_frames()])
        self.canvas.draw()
        
    def calculate_center_point(self, dataBase, dataOverlap, point_name):
        if point_name == "waistCenter":
            point1_name = "leftHip"
            point2_name = "rightHip"
        elif point_name == "shoulderCenter":
            point1_name = "leftShoulder"
            point2_name = "rightShoulder"
        dataBase[f"{point_name}X Base"] = (dataBase[f"{point1_name}X Base"] + dataBase[f"{point2_name}X Base"]) / 2
        dataBase[f"{point_name}Y Base"] = (dataBase[f"{point1_name}Y Base"] + dataBase[f"{point2_name}Y Base"]) / 2
        dataOverlap[f"{point_name}X Overlap"] = (dataOverlap[f"{point1_name}X Overlap"] + dataOverlap[f"{point2_name}X Overlap"]) / 2
        dataOverlap[f"{point_name}Y Overlap"] = (dataOverlap[f"{point1_name}Y Overlap"] + dataOverlap[f"{point2_name}Y Overlap"]) / 2

        
    # def getCenter(a, b):
    #     return [(x + y) / 2 for x, y in zip(a, b)]
        
    def update_ui(self):
        if self.comboBox.currentText() == "positionX" or self.comboBox.currentText() == "positionY":
            self.pointAComboBox.show()
            self.pointBComboBox.hide()
            self.pointCComboBox.hide()
            self.pointAComboBoxLabel.show()
            self.pointBComboBoxLabel.hide()
            self.pointCComboBoxLabel.hide()
        elif self.comboBox.currentText() == "angle":
            self.pointAComboBox.show()
            self.pointBComboBox.show()
            self.pointCComboBox.show()
            self.pointAComboBoxLabel.show()
            self.pointBComboBoxLabel.show()
            self.pointCComboBoxLabel.show()
        self.update_graph()

class SingleVideoPlayer(QWidget):
    def __init__(self, parent=None, video_file_path=None):
        super().__init__(parent)
        
        self.cap = None
        self.currentFrame = None
        self.fps = 0
        self.totalFrames = 0

        self.layout = QVBoxLayout(self)
        self.topLayout = QHBoxLayout()
        self.infoLabel = QLabel(self)
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.topLayout.addWidget(self.infoLabel)
        self.layout.addLayout(self.topLayout)

        self.graphicsView = QGraphicsView(self)
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setMinimumHeight(400)
        self.layout.addWidget(self.graphicsView)

        self.controlLayout = QHBoxLayout()
        self.playButton = QPushButton("▶", self)  
        self.playButton.clicked.connect(self.startPlay)
        self.controlLayout.addWidget(self.playButton)

        self.resumeButton = QPushButton("⏯", self)  
        self.resumeButton.clicked.connect(self.resumePlay)
        self.controlLayout.addWidget(self.resumeButton)

        self.stopButton = QPushButton("⏹", self)  
        self.stopButton.clicked.connect(self.stopPlay)
        self.controlLayout.addWidget(self.stopButton)

        self.layout.addLayout(self.controlLayout)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.setPosition)
        self.layout.addWidget(self.slider)
            
        if video_file_path:
            self.cap = cv2.VideoCapture(video_file_path)
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.totalFrames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.setRange(0, self.totalFrames)
            
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.updateFrame)
            self.timer.start(int(1000 / self.fps))
        else:
            return

    def updateFrame(self):
        ret, frame = self.cap.read()
        if ret:
            self.currentFrame = frame
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qImg)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.graphicsView.setScene(self.scene)
            self.graphicsView.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.updateInfoLabel()
            self.slider.setValue(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
        else:
            self.timer.stop()

    def startPlay(self):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.timer.start(int(1000 / self.fps))

    def resumePlay(self):
        if self.cap:
            self.timer.start(int(1000 / self.fps))

    def stopPlay(self):
        self.timer.stop()

    def setPosition(self, position):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            ret, frame = self.cap.read()
            if ret:
                self.currentFrame = frame
                height, width, channel = frame.shape
                bytesPerLine = 3 * width
                qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format.Format_RGB888).rgbSwapped()
                pixmap = QPixmap.fromImage(qImg)
                self.scene.clear()
                self.scene.addPixmap(pixmap)
                self.graphicsView.setScene(self.scene)
                self.graphicsView.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
                self.updateInfoLabel()
            else:
                self.timer.stop()

    def updateInfoLabel(self):
        currentFrameNum = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.infoLabel.setText(f"FPS: {self.fps} | Total Frames: {self.totalFrames} | Current Frame: {currentFrameNum}")

    def get_current_frame(self):
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def get_total_frames(self):
        return self.totalFrames
