import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget,QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSlider, QLabel, QSizePolicy, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QLineEdit, QComboBox
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QProgressDialog, QErrorMessage


import pose_detection
import generate_video_with_bone
import generated_video_player


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.players_layout = QHBoxLayout()

        self.player1 = SingleVideoPlayer(self, True)
        self.players_layout.addWidget(self.player1)

        self.player2 = SingleVideoPlayer(self, False)
        self.players_layout.addWidget(self.player2)

        self.layout.addLayout(self.players_layout)

        self.functions_layout = QHBoxLayout()

        self.close_button = QPushButton(" Close ", self)
        self.close_button.setFixedSize(self.close_button.sizeHint())
        self.close_button.clicked.connect(self.close)
        self.functions_layout.addWidget(self.close_button)

        self.functions_layout.addStretch(1)

        self.output_video_file_name_label = QLabel("Output File Name", self)
        self.functions_layout.addWidget(self.output_video_file_name_label)

        self.output_video_file_name_input = QLineEdit(self)
        self.output_video_file_name_input.setFixedWidth(320)
        self.output_video_file_name_input.setStyleSheet("QLineEdit { border-radius: 5px; }")
        self.functions_layout.addWidget(self.output_video_file_name_input)

        self.generate_button = QPushButton(" Generate Video ", self)
        self.generate_button.clicked.connect(self.generate_video)
        self.generate_button.setFixedSize(self.generate_button.sizeHint())
        self.functions_layout.addWidget(self.generate_button)

        self.layout.addLayout(self.functions_layout)

        self.setLayout(self.layout)
        self.setWindowTitle("Movement Comparison Video Generator")
        self.resize(1600, 600)

    def generate_video(self):
        video_file_path = self.player1.get_video_file_path()
        video_file_path2 = self.player2.get_video_file_path()

        if video_file_path == "" or video_file_path2 == "":
            self.error_dialog = QErrorMessage(self)
            self.error_dialog.setWindowTitle("Error")
            self.error_dialog.showMessage("Please select video file.")
            self.error_dialog.setWindowModality(Qt.WindowModality.WindowModal)

            self.error_dialog.show()
            return

        self.progress_dialog = QProgressDialog("Processing...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Please Wait")
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()
        QApplication.processEvents()

        csv_path = f"exported/{video_file_path.split('/')[-1].split('.')[-2]}.csv"
        csv_path2 = f"exported/{video_file_path2.split('/')[-1].split('.')[-2]}.csv"

        target_fps = self.player2.get_video_fps()

        output_video_file_name = self.output_video_file_name_input.text()
        color1 = self.player1.get_selected_color()
        color2 = self.player2.get_selected_color()

        overlap_frame_base = self.player1.get_overlap_frame()
        overlap_frame_target = self.player2.get_overlap_frame()

        if overlap_frame_base is None or overlap_frame_target is None:
            self.error_dialog = QErrorMessage(self)
            self.error_dialog.setWindowTitle("Error")
            self.error_dialog.showMessage("Overlap Frame is invalid.")
            self.error_dialog.show()
            self.progress_dialog.close()
            return

        overlap_body_part_base = self.player1.overlap_body_part_combo_box.currentText()
        overlap_body_part_target = self.player2.overlap_body_part_combo_box.currentText()

        generated_video_path, generated_csv_path = generate_video_with_bone.generate_download_video(
            video_file_path, csv_path, csv_path2, target_fps, overlap_frame_base,
            overlap_frame_target, overlap_body_part_base, overlap_body_part_target,
            color1, color2, output_video_file_name
        )

        self.progress_dialog.close()

        self.generated_video_view = generated_video_player.GeneratedVideoPlayer(generated_video_path, generated_csv_path)
        self.generated_video_view.show()

class SingleVideoPlayer(QWidget):
    def __init__(self, parent=None, is_base=False):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.top_layout = QHBoxLayout()

        if is_base:
            self.open_button = QPushButton(" Select Base Video", self)
        else:
            self.open_button = QPushButton(" Select Overlap Video", self)

        self.open_button.clicked.connect(self.open_file)
        self.open_button.setFixedSize(self.open_button.sizeHint())
        self.top_layout.addWidget(self.open_button)

        self.info_label = QLabel(self)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.top_layout.addWidget(self.info_label)

        self.layout.addLayout(self.top_layout)

        self.graphics_view = QGraphicsView(self)
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.layout.addWidget(self.graphics_view)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

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

        self.setting_layout = QHBoxLayout()
        self.setting_layout.addStretch(1)

        self.overlap_frame_input_label = QLabel("Overlap Frame", self)
        self.setting_layout.addWidget(self.overlap_frame_input_label)

        self.overlap_frame_input = QLineEdit(self)
        self.overlap_frame_input.setFixedWidth(80)
        self.overlap_frame_input.setStyleSheet("QLineEdit { border-radius: 5px; }")
        self.setting_layout.addWidget(self.overlap_frame_input)

        self.overlap_body_part_label = QLabel("Overlap Body Part", self)
        self.setting_layout.addWidget(self.overlap_body_part_label)

        self.overlap_body_part_combo_box = QComboBox(self)
        self.overlap_body_part_combo_box.addItems(generate_video_with_bone.body_parts_mapping.keys())
        self.overlap_body_part_combo_box.setFixedWidth(120)
        self.setting_layout.addWidget(self.overlap_body_part_combo_box)

        self.output_video_file_name_label = QLabel("Bone Color", self)
        self.setting_layout.addWidget(self.output_video_file_name_label)

        self.color_combo_box = QComboBox(self)
        self.color_combo_box.addItems(["red", "blue", "green", "yellow", "white", "black"])
        self.color_combo_box.setFixedWidth(100)
        self.setting_layout.addWidget(self.color_combo_box)

        self.layout.addLayout(self.setting_layout)

        self.cap = None
        self.current_frame = None
        self.fps = 0
        self.total_frames = 0
        self.video_file_path = ""

    def open_file(self):
        self.video_file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Movie", "", "All Files (*);;Movie Files (*.mp4 *.avi)")
        
        # getOpenFileNameでファイルが選択されなかった場合
        if self.video_file_path == "":
            return
        
        # プログレスダイアログの設定
        self.progressDialog = QProgressDialog("Processing...", None, 0, 0, self)
        self.progressDialog.setWindowTitle("Please Wait")
        self.progressDialog.setModal(True)  # 他のウィンドウの操作をブロック
        self.progressDialog.show()
        QApplication.processEvents()  # UIを更新
        
        csv_path = pose_detection.pose_detection(self.video_file_path)
        generated_video_path, generated_csv_path = generate_video_with_bone.generate_download_video(self.video_file_path, csv_path, "", 60, 0, 0, "waistCenter", "waistCenter", self.color_combo_box.currentText(), "blue", "")
        
        if generated_video_path:
            self.cap = cv2.VideoCapture(generated_video_path)
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.totalFrames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.setRange(0, self.totalFrames)
            self.timer.start(int(1000 / self.fps))
            
        # プログレスダイアログを閉じる
        self.progressDialog.close()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.currentFrame = frame
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qImg = QImage(frame.data, width, height, bytesPerLine,
                          QImage.Format.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qImg)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.graphics_view.setScene(self.scene)
            self.graphics_view.fitInView(
                self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.update_info_label()
            self.slider.setValue(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
        else:
            self.timer.stop()

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
            ret, frame = self.cap.read()
            if ret:
                self.currentFrame = frame
                height, width, channel = frame.shape
                bytesPerLine = 3 * width
                qImg = QImage(frame.data, width, height, bytesPerLine,
                              QImage.Format.Format_RGB888).rgbSwapped()
                pixmap = QPixmap.fromImage(qImg)
                self.scene.clear()
                self.scene.addPixmap(pixmap)
                self.graphics_view.setScene(self.scene)
                self.graphics_view.fitInView(
                    self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
                self.update_info_label()
            else:
                self.timer.stop()

    def update_info_label(self):
        currentFrameNum = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.info_label.setText(
            f"FPS: {self.fps} | Total Frames: {self.totalFrames} | Current Frame: {currentFrameNum}")
        
    def get_video_file_path(self):
        return self.video_file_path
    
    def get_current_frame(self):
        currentFrameNum = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        return currentFrameNum
    
    def get_video_fps(self):
        return self.fps
    
    def get_overlap_frame(self):
        try:
            overlap_frame = int(self.overlap_frame_input.text())
            if 0 <= overlap_frame and overlap_frame <= self.totalFrames:
                return overlap_frame
            else:
                return None
        except:
            return None
    
    def get_selected_color(self):
        return self.color_combo_box.currentText()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
