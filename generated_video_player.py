import sys
import cv2
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QComboBox, QCheckBox)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QFont
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
        
         # チェックボックスの追加
        self.pointCheckBoxLayout = QHBoxLayout()
        self.pointCheckBoxLayout.addStretch(1)
        self.baseCheckBox = QCheckBox("Show Base Select Points", self)
        self.baseCheckBox.setChecked(True)
        self.targetCheckBox = QCheckBox("Show Target Select Points", self)
        self.targetCheckBox.setChecked(True)
        self.pointComboBoxLayout.addWidget(self.baseCheckBox)
        self.pointComboBoxLayout.addWidget(self.targetCheckBox)
        
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

        self.baseCheckBox.stateChanged.connect(self.update_graph)
        self.targetCheckBox.stateChanged.connect(self.update_graph)
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
        show_base = self.baseCheckBox.isChecked()
        show_target = self.targetCheckBox.isChecked()
        self.player1.set_show_points(show_base, show_target)
        
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
        
        current_frame = self.player1.get_current_frame() - 1
        if self.comboBox.currentText() == "positionX":
            if current_frame < len(base_dataX):
                    current_value_base = base_dataX[current_frame]
                    self.ax.scatter([current_frame], [current_value_base], color='b')
                    self.ax.text(0.98, 0.92, f"Base: {current_value_base:.2f}", transform=self.ax.transAxes,
                             verticalalignment='top', horizontalalignment='right', color='b')
            if current_frame < len(overlap_dataX):
                current_value_overlap = overlap_dataX[current_frame]
                self.ax.scatter([current_frame], [current_value_overlap], color='orange')
                self.ax.text(0.98, 0.8, f"Overlap: {current_value_overlap:.2f}", transform=self.ax.transAxes,
                             verticalalignment='top', horizontalalignment='right', color='orange')
        elif self.comboBox.currentText() == "positionY":
            if current_frame < len(base_dataY):
                current_value_base = base_dataY[current_frame]
                self.ax.scatter([current_frame], [current_value_base], color='b')
                self.ax.text(0.98, 0.92, f"Base: {current_value_base:.2f}", transform=self.ax.transAxes,
                             verticalalignment='top', horizontalalignment='right', color='b')
            if current_frame < len(overlap_dataY):
                current_value_overlap = overlap_dataY[current_frame]
                self.ax.scatter([current_frame], [current_value_overlap], color='orange')
                self.ax.text(0.98, 0.8, f"Overlap: {current_value_overlap:.2f}", transform=self.ax.transAxes,
                             verticalalignment='top', horizontalalignment='right', color='orange')
                
        elif self.comboBox.currentText() == "angle":
            if current_frame < len(angles_base):
                current_value_base = angles_base[current_frame]
                self.ax.scatter([current_frame], [current_value_base], color='b')
                self.ax.text(0.98, 0.92, f"Base: {current_value_base:.2f}", transform=self.ax.transAxes,
                             verticalalignment='top', horizontalalignment='right', color='b')
            if current_frame < len(angles_overlap):
                current_value_overlap = angles_overlap[current_frame]
                self.ax.scatter([current_frame], [current_value_overlap], color='orange')
                self.ax.text(0.98, 0.8, f"Overlap: {current_value_overlap:.2f}", transform=self.ax.transAxes,
                             verticalalignment='top', horizontalalignment='right', color='orange')

        self.ax.axvline(x=self.player1.get_current_frame() - 1, color='r', linestyle='--')
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
        self.draw_points = {}
        self.show_base = False
        self.show_target = False

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
            self.timer.timeout.connect(self.nextFrame)
            self.timer.start(int(1000 / self.fps))
        else:
            return
        
    def nextFrame(self):
        self.updateFrame()
        self.slider.setValue(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))

    def updateFrame(self):
        ret, frame = self.cap.read()
        if ret:
            self.currentFrame = frame
            height, width, channel = frame.shape
            bytesPerLine = 3 * width

            # ここで、親ウィジェットから選択されたポイントの座標を取得します。
            pointA_name = self.parent().pointAComboBox.currentText()
            if pointA_name == "waistCenter" or pointA_name == "shoulderCenter":
                self.parent().calculate_center_point(self.parent().base_data, self.parent().overlap_data, pointA_name)
            
            current_frame_num = self.get_current_frame() - 1

            # pointAに円を描画します。
            if self.show_base:
                if current_frame_num < len(self.parent().base_data):
                    pointA_coord_base = self.parent().base_data.loc[current_frame_num, [f"{pointA_name}X Base", f"{pointA_name}Y Base"]].values
                    cv2.circle(frame, (int(pointA_coord_base[0]), int(pointA_coord_base[1])), radius=12, color=(255, 0, 0), thickness=-4)
            if self.show_target:
                if current_frame_num < len(self.parent().overlap_data):
                    pointA_coord_overlap = self.parent().overlap_data.loc[current_frame_num, [f"{pointA_name}X Overlap", f"{pointA_name}Y Overlap"]].values
                    cv2.circle(frame, (int(pointA_coord_overlap[0]), int(pointA_coord_overlap[1])), radius=12, color=(0, 128, 255), thickness=-4)
                

            # angleが選択されている場合、追加のポイントと線分を描画します。
            if self.parent().comboBox.currentText() == "angle":
                pointB_name = self.parent().pointBComboBox.currentText()
                pointC_name = self.parent().pointCComboBox.currentText()
                
                if pointB_name == "waistCenter" or pointB_name == "shoulderCenter":
                    self.parent().calculate_center_point(self.parent().base_data, self.parent().overlap_data, pointB_name)
                if pointC_name == "waistCenter" or pointC_name == "shoulderCenter":
                    self.parent().calculate_center_point(self.parent().base_data, self.parent().overlap_data, pointC_name)

                if self.show_base:
                    if current_frame_num < len(self.parent().base_data):
                        pointB_coord_base = self.parent().base_data.loc[current_frame_num, [f"{pointB_name}X Base", f"{pointB_name}Y Base"]].values
                        cv2.circle(frame, (int(pointB_coord_base[0]), int(pointB_coord_base[1])), radius=12, color=(255, 0, 0), thickness=-4)
                        cv2.line(frame, (int(pointA_coord_base[0]), int(pointA_coord_base[1])), (int(pointB_coord_base[0]), int(pointB_coord_base[1])), (255, 0, 0), 2)
                        
                        if pointC_name != "horizontal":
                            pointC_coord_base = self.parent().base_data.loc[current_frame_num, [f"{pointC_name}X Base", f"{pointC_name}Y Base"]].values
                            cv2.circle(frame, (int(pointC_coord_base[0]), int(pointC_coord_base[1])), radius=12, color=(255, 0, 0), thickness=-4)
                            cv2.line(frame, (int(pointB_coord_base[0]), int(pointB_coord_base[1])), (int(pointC_coord_base[0]), int(pointC_coord_base[1])), (255, 0, 0), 2)
                    
                if self.show_target:
                    if current_frame_num < len(self.parent().overlap_data):
                        pointB_coord_overlap = self.parent().overlap_data.loc[current_frame_num, [f"{pointB_name}X Overlap", f"{pointB_name}Y Overlap"]].values
                        cv2.circle(frame, (int(pointB_coord_overlap[0]), int(pointB_coord_overlap[1])), radius=12, color=(0, 128, 255), thickness=-4)
                        cv2.line(frame, (int(pointA_coord_overlap[0]), int(pointA_coord_overlap[1])), (int(pointB_coord_overlap[0]), int(pointB_coord_overlap[1])), (0, 128, 255), 2)
                        if pointC_name != "horizontal":
                            pointC_coord_overlap = self.parent().overlap_data.loc[current_frame_num, [f"{pointC_name}X Overlap", f"{pointC_name}Y Overlap"]].values
                            cv2.circle(frame, (int(pointC_coord_overlap[0]), int(pointC_coord_overlap[1])), radius=12, color=(0, 128, 255), thickness=-4)
                            cv2.line(frame, (int(pointB_coord_overlap[0]), int(pointB_coord_overlap[1])), (int(pointC_coord_overlap[0]), int(pointC_coord_overlap[1])), (0, 128, 255), 2)
                

            qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qImg)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.graphicsView.setScene(self.scene)
            self.graphicsView.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.updateInfoLabel()
        else:
            self.timer.stop()
            
    def set_show_points(self, show_base, show_target):
        self.show_base = show_base
        self.show_target = show_target
        self.updateFrame()


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
            self.updateFrame()

    def updateInfoLabel(self):
        currentFrameNum = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.infoLabel.setText(f"FPS: {self.fps} | Total Frames: {self.totalFrames} | Current Frame: {currentFrameNum}")

    def get_current_frame(self):
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def get_total_frames(self):
        return self.totalFrames
