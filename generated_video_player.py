import cv2
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider,
    QLabel, QGraphicsView, QGraphicsScene, QComboBox, QCheckBox
)
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

        self.select_chart_type_layout = QHBoxLayout()
        self.select_chart_type_layout.addStretch(1)
        self.select_chart_type_label = QLabel("Chart Type", self)
        self.select_chart_type_layout.addWidget(self.select_chart_type_label)

        self.combo_box = QComboBox(self)
        self.combo_box.addItem("positionX")
        self.combo_box.addItem("positionY")
        self.combo_box.addItem("angle")
        self.select_chart_type_layout.addWidget(self.combo_box)

        self.layout.addLayout(self.select_chart_type_layout)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.data = pd.read_csv(csv_path)
        self.base_data = self.data.filter(regex=" Base$")
        self.overlap_data = self.data.filter(regex=" Overlap$")

        self.point_combo_box_layout = QHBoxLayout()
        self.point_check_box_layout = QHBoxLayout()
        self.point_check_box_layout.addStretch(1)
        self.base_check_box = QCheckBox("Show Base Select Points", self)
        self.base_check_box.setChecked(True)
        self.target_check_box = QCheckBox("Show Target Select Points", self)
        self.target_check_box.setChecked(True)
        self.point_combo_box_layout.addWidget(self.base_check_box)
        self.point_combo_box_layout.addWidget(self.target_check_box)

        self.point_combo_box_layout.addStretch(1)
        self.point_a_combo_box_label = QLabel("pointa", self)
        self.point_combo_box_layout.addWidget(self.point_a_combo_box_label)
        self.point_a_combo_box = QComboBox(self)
        self.point_combo_box_layout.addWidget(self.point_a_combo_box)

        self.point_b_combo_box_label = QLabel("point_b", self)
        self.point_combo_box_layout.addWidget(self.point_b_combo_box_label)
        self.point_b_combo_box = QComboBox(self)
        self.point_combo_box_layout.addWidget(self.point_b_combo_box)

        self.point_c_combo_box_label = QLabel("point_c", self)
        self.point_combo_box_layout.addWidget(self.point_c_combo_box_label)
        self.point_c_combo_box = QComboBox(self)
        self.point_combo_box_layout.addWidget(self.point_c_combo_box)

        body_parts = list(dict.fromkeys([col.split(' ')[0][:-1] for col in self.base_data.columns]))
        body_parts.extend(['waistCenter', 'shoulderCenter'])

        self.point_a_combo_box.addItems(body_parts)
        self.point_b_combo_box.addItems(body_parts)
        self.point_c_combo_box.addItems(body_parts + ['horizontal'])

        self.layout.addLayout(self.point_combo_box_layout)

        self.base_check_box.stateChanged.connect(self.update_graph)
        self.target_check_box.stateChanged.connect(self.update_graph)
        self.combo_box.currentIndexChanged.connect(self.update_graph)
        self.point_a_combo_box.currentIndexChanged.connect(self.update_graph)
        self.point_b_combo_box.currentIndexChanged.connect(self.update_graph)
        self.point_c_combo_box.currentIndexChanged.connect(self.update_graph)
        self.player1.slider.valueChanged.connect(self.update_graph)

        self.combo_box.currentIndexChanged.connect(self.update_ui)

        self.setLayout(self.layout)
        self.setWindowTitle("Movement Comparison Video Generator")
        self.resize(1600, 900)

        self.update_graph()
        self.update_ui()

    def calculate_angle_between_three_points(self, point_a, point_b, point_c):
        vector_ab = point_b - point_a
        vector_bc = point_c - point_b

        dot_product = np.sum(vector_ab * vector_bc, axis=1)
        norm_ab = np.linalg.norm(vector_ab, axis=1)
        norm_bc = np.linalg.norm(vector_bc, axis=1)

        angles_rad = np.arccos(dot_product / (norm_ab * norm_bc))
        angles_deg = np.degrees(angles_rad)

        return 180 - angles_deg

    def update_graph(self):
        show_base = self.base_check_box.isChecked()
        show_target = self.target_check_box.isChecked()
        self.player1.set_show_points(show_base, show_target)

        self.ax.clear()
        if self.combo_box.currentText() == "positionX":
            part_name = self.point_a_combo_box.currentText()
            
            if part_name == "waistCenter" or part_name == "shoulderCenter":
                self.calculate_center_point(self.base_data, self.overlap_data, part_name)

            base_dataX = self.base_data[f"{part_name}X Base"].values
            overlap_dataX = self.overlap_data[f"{part_name}X Overlap"].values
            
            self.ax.plot(base_dataX, label="Base")
            self.ax.plot(overlap_dataX, label="Overlap")
        elif self.combo_box.currentText() == "positionY":
            part_name = self.point_a_combo_box.currentText()
            
            if part_name == "waistCenter" or part_name == "shoulderCenter":
                self.calculate_center_point(self.base_data, self.overlap_data, part_name)
            
            base_dataY = self.base_data[f"{part_name}Y Base"].values
            overlap_dataY = self.overlap_data[f"{part_name}Y Overlap"].values
            
            self.ax.plot(base_dataY, label="Base")
            self.ax.plot(overlap_dataY, label="Overlap")
        elif self.combo_box.currentText() == "angle":
            pointa_name = self.point_a_combo_box.currentText()
            point_b_name = self.point_b_combo_box.currentText()
            point_c_name = self.point_c_combo_box.currentText()
            
            if pointa_name == "waistCenter" or pointa_name == "shoulderCenter":
                self.calculate_center_point(self.base_data, self.overlap_data, pointa_name)
                
            if point_b_name == "waistCenter" or point_b_name == "shoulderCenter":
                self.calculate_center_point(self.base_data, self.overlap_data, point_b_name)
            if point_c_name == "waistCenter" or point_c_name == "shoulderCenter":
                self.calculate_center_point(self.base_data, self.overlap_data, point_c_name)
            
            pointa_base = self.base_data[[f"{pointa_name}X Base", f"{pointa_name}Y Base"]].values
            point_b_base = self.base_data[[f"{point_b_name}X Base", f"{point_b_name}Y Base"]].values
            pointa_overlap = self.overlap_data[[f"{pointa_name}X Overlap", f"{pointa_name}Y Overlap"]].values
            point_b_overlap = self.overlap_data[[f"{point_b_name}X Overlap", f"{point_b_name}Y Overlap"]].values
            
            if point_c_name == "horizontal":
                point_c_base = np.copy(point_b_base)
                point_c_base[:, 0] = 0  # Y座標を0にして水平線を表現
                point_c_overlap = np.copy(point_b_overlap)
                point_c_overlap[:, 0] = 0  # Y座標を0にして水平線を表現
            else:
                point_c_base = self.base_data[[f"{point_c_name}X Base", f"{point_c_name}Y Base"]].values
                point_c_overlap = self.overlap_data[[f"{point_c_name}X Overlap", f"{point_c_name}Y Overlap"]].values
            
            angles_base = self.calculate_angle_between_three_points(pointa_base, point_b_base, point_c_base)
            self.ax.plot(angles_base, label="Base")
            angles_overlap = self.calculate_angle_between_three_points(pointa_overlap, point_b_overlap, point_c_overlap)
            self.ax.plot(angles_overlap, label="Overlap")
        
        current_frame = self.player1.get_current_frame() - 1
        if self.combo_box.currentText() == "positionX":
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
        elif self.combo_box.currentText() == "positionY":
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
                
        elif self.combo_box.currentText() == "angle":
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
        
    def calculate_center_point(self, data_base, data_overlap, point_name):
        if point_name == "waistCenter":
            point1_name = "leftHip"
            point2_name = "rightHip"
        elif point_name == "shoulderCenter":
            point1_name = "leftShoulder"
            point2_name = "rightShoulder"
        data_base[f"{point_name}X Base"] = (data_base[f"{point1_name}X Base"] + data_base[f"{point2_name}X Base"]) / 2
        data_base[f"{point_name}Y Base"] = (data_base[f"{point1_name}Y Base"] + data_base[f"{point2_name}Y Base"]) / 2
        data_overlap[f"{point_name}X Overlap"] = (data_overlap[f"{point1_name}X Overlap"] + data_overlap[f"{point2_name}X Overlap"]) / 2
        data_overlap[f"{point_name}Y Overlap"] = (data_overlap[f"{point1_name}Y Overlap"] + data_overlap[f"{point2_name}Y Overlap"]) / 2
        
    def update_ui(self):
        if self.combo_box.currentText() == "positionX" or self.combo_box.currentText() == "positionY":
            self.point_a_combo_box.show()
            self.point_b_combo_box.hide()
            self.point_c_combo_box.hide()
            self.point_a_combo_box_label.show()
            self.point_b_combo_box_label.hide()
            self.point_c_combo_box_label.hide()
        elif self.combo_box.currentText() == "angle":
            self.point_a_combo_box.show()
            self.point_b_combo_box.show()
            self.point_c_combo_box.show()
            self.point_a_combo_box_label.show()
            self.point_b_combo_box_label.show()
            self.point_c_combo_box_label.show()
        self.update_graph()

class SingleVideoPlayer(QWidget):
    def __init__(self, parent=None, video_file_path=None):
        super().__init__(parent)

        self.cap = None
        self.current_frame = None
        self.fps = 0
        self.total_frames = 0
        self.draw_points = {}
        self.show_base = False
        self.show_target = False

        self.layout = QVBoxLayout(self)
        self.top_layout = QHBoxLayout()
        self.info_label = QLabel(self)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.top_layout.addWidget(self.info_label)
        self.layout.addLayout(self.top_layout)

        self.graphics_view = QGraphicsView(self)
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.graphics_view.setMinimumHeight(400)
        self.layout.addWidget(self.graphics_view)

        self.control_layout = QHBoxLayout()
        self.play_button = QPushButton("▶", self)
        self.play_button.clicked.connect(self.start_play)
        self.control_layout.addWidget(self.play_button)

        self.resume_button = QPushButton("⏯", self)
        self.resume_button.clicked.connect(self.resume_play)
        self.control_layout.addWidget(self.resume_button)

        self.stop_button = QPushButton("⏹", self)
        self.stop_button.clicked.connect(self.stop_play)
        self.control_layout.addWidget(self.stop_button)

        self.layout.addLayout(self.control_layout)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.set_position)
        self.layout.addWidget(self.slider)

        if video_file_path:
            self.cap = cv2.VideoCapture(video_file_path)
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.setRange(0, self.total_frames)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.next_frame)
            self.timer.start(int(1000 / self.fps))
        else:
            return
        
    def next_frame(self):
        self.update_frame()
        self.slider.setValue(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.currentFrame = frame
            height, width, channel = frame.shape
            bytesPerLine = 3 * width

            # ここで、親ウィジェットから選択されたポイントの座標を取得します。
            pointa_name = self.parent().point_a_combo_box.currentText()
            if pointa_name == "waistCenter" or pointa_name == "shoulderCenter":
                self.parent().calculate_center_point(self.parent().base_data, self.parent().overlap_data, pointa_name)
            
            current_frame_num = self.get_current_frame() - 1

            # pointaに円を描画します。
            if self.show_base:
                if current_frame_num < len(self.parent().base_data):
                    pointa_coord_base = self.parent().base_data.loc[current_frame_num, [f"{pointa_name}X Base", f"{pointa_name}Y Base"]].values
                    cv2.circle(frame, (int(pointa_coord_base[0]), int(pointa_coord_base[1])), radius=12, color=(255, 0, 0), thickness=-4)
            if self.show_target:
                if current_frame_num < len(self.parent().overlap_data):
                    pointa_coord_overlap = self.parent().overlap_data.loc[current_frame_num, [f"{pointa_name}X Overlap", f"{pointa_name}Y Overlap"]].values
                    cv2.circle(frame, (int(pointa_coord_overlap[0]), int(pointa_coord_overlap[1])), radius=12, color=(0, 128, 255), thickness=-4)
                

            # angleが選択されている場合、追加のポイントと線分を描画します。
            if self.parent().combo_box.currentText() == "angle":
                point_b_name = self.parent().point_b_combo_box.currentText()
                point_c_name = self.parent().point_c_combo_box.currentText()
                
                if point_b_name == "waistCenter" or point_b_name == "shoulderCenter":
                    self.parent().calculate_center_point(self.parent().base_data, self.parent().overlap_data, point_b_name)
                if point_c_name == "waistCenter" or point_c_name == "shoulderCenter":
                    self.parent().calculate_center_point(self.parent().base_data, self.parent().overlap_data, point_c_name)

                if self.show_base:
                    if current_frame_num < len(self.parent().base_data):
                        point_b_coord_base = self.parent().base_data.loc[current_frame_num, [f"{point_b_name}X Base", f"{point_b_name}Y Base"]].values
                        cv2.circle(frame, (int(point_b_coord_base[0]), int(point_b_coord_base[1])), radius=12, color=(255, 0, 0), thickness=-4)
                        cv2.line(frame, (int(pointa_coord_base[0]), int(pointa_coord_base[1])), (int(point_b_coord_base[0]), int(point_b_coord_base[1])), (255, 0, 0), 2)
                        
                        if point_c_name != "horizontal":
                            point_c_coord_base = self.parent().base_data.loc[current_frame_num, [f"{point_c_name}X Base", f"{point_c_name}Y Base"]].values
                            cv2.circle(frame, (int(point_c_coord_base[0]), int(point_c_coord_base[1])), radius=12, color=(255, 0, 0), thickness=-4)
                            cv2.line(frame, (int(point_b_coord_base[0]), int(point_b_coord_base[1])), (int(point_c_coord_base[0]), int(point_c_coord_base[1])), (255, 0, 0), 2)
                    
                if self.show_target:
                    if current_frame_num < len(self.parent().overlap_data):
                        point_b_coord_overlap = self.parent().overlap_data.loc[current_frame_num, [f"{point_b_name}X Overlap", f"{point_b_name}Y Overlap"]].values
                        cv2.circle(frame, (int(point_b_coord_overlap[0]), int(point_b_coord_overlap[1])), radius=12, color=(0, 128, 255), thickness=-4)
                        cv2.line(frame, (int(pointa_coord_overlap[0]), int(pointa_coord_overlap[1])), (int(point_b_coord_overlap[0]), int(point_b_coord_overlap[1])), (0, 128, 255), 2)
                        if point_c_name != "horizontal":
                            point_c_coord_overlap = self.parent().overlap_data.loc[current_frame_num, [f"{point_c_name}X Overlap", f"{point_c_name}Y Overlap"]].values
                            cv2.circle(frame, (int(point_c_coord_overlap[0]), int(point_c_coord_overlap[1])), radius=12, color=(0, 128, 255), thickness=-4)
                            cv2.line(frame, (int(point_b_coord_overlap[0]), int(point_b_coord_overlap[1])), (int(point_c_coord_overlap[0]), int(point_c_coord_overlap[1])), (0, 128, 255), 2)
                

            qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qImg)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.graphics_view.setScene(self.scene)
            self.graphics_view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.update_info_label()
        else:
            self.timer.stop()
            
    def set_show_points(self, show_base, show_target):
        self.show_base = show_base
        self.show_target = show_target
        self.update_frame()


    def start_play(self):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.timer.start(int(1000 / self.fps))

    def resume_play(self):
        if self.cap:
            self.timer.start(int(1000 / self.fps))

    def stop_play(self):
        self.timer.stop()

    def set_position(self, position):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            self.update_frame()

    def update_info_label(self):
        currentFrameNum = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.info_label.setText(f"FPS: {self.fps} | Total Frames: {self.total_frames} | Current Frame: {currentFrameNum}")

    def get_current_frame(self):
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def get_total_frames(self):
        return self.total_frames
