import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget,QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSlider, QLabel, QSizePolicy, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QLineEdit, QComboBox
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QProgressDialog, QErrorMessage


import pose_detection
import generate_video_with_bone


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # メインレイアウトの設定
        self.layout = QVBoxLayout(self)

        # 2つの動画プレイヤーのレイアウト
        self.playersLayout = QHBoxLayout()

        # 1つ目の動画プレイヤーの設定
        self.player1 = SingleVideoPlayer(self, True)
        self.playersLayout.addWidget(self.player1)

        # 2つ目の動画プレイヤーの設定
        self.player2 = SingleVideoPlayer(self, False)
        self.playersLayout.addWidget(self.player2)

        self.layout.addLayout(self.playersLayout)
        
        
        self.functionsLayout = QHBoxLayout() 

        # 閉じるボタンの設定
        self.closeButton = QPushButton(" Close ", self)
        self.closeButton.setFixedSize(
            self.closeButton.sizeHint())  # ボタンの横幅を文字がちょうど収まる程度に設定
        self.closeButton.clicked.connect(self.close)
        self.functionsLayout.addWidget(self.closeButton)
        
        self.functionsLayout.addStretch(1)
        
        # 文字列を表示
        self.output_video_file_name_label = QLabel("Output File Name", self)
        self.functionsLayout.addWidget(self.output_video_file_name_label)
        
        # 文字列を入力できる入力欄の設定
        self.output_video_file_name_input = QLineEdit(self)
        self.output_video_file_name_input.setFixedWidth(320)
        self.output_video_file_name_input.setStyleSheet("QLineEdit { border-radius: 5px; }")
        self.functionsLayout.addWidget(self.output_video_file_name_input)

        # 動画生成ボタンの設定
        self.generateButton = QPushButton(" Generate Video ", self)
        self.generateButton.clicked.connect(self.generateVideo)
        self.generateButton.setFixedSize(
            self.generateButton.sizeHint())  # ボタンの横幅を文字がちょうど収まる程度に設定
        self.functionsLayout.addWidget(self.generateButton)

        self.layout.addLayout(self.functionsLayout)

        # ウィンドウの設定
        self.setLayout(self.layout)
        self.setWindowTitle("Movement Comparison Video Generator")
        self.resize(1600, 600)

    def generateVideo(self):
        video_file_path = self.player1.get_video_file_path()
        video_file_path2 = self.player2.get_video_file_path()
        
        if video_file_path == "" or video_file_path2 == "":
            self.errorDialog = QErrorMessage(self)
            self.errorDialog.setWindowTitle("Error")
            self.errorDialog.showMessage("Please select video file.")
            # Show this message againを表示しない
            self.errorDialog.setWindowModality(Qt.WindowModality.WindowModal)
            
            self.errorDialog.show()
            return
        
        # プログレスダイアログの設定
        self.progressDialog = QProgressDialog("Processing...", None, 0, 0, self)
        self.progressDialog.setWindowTitle("Please Wait")
        self.progressDialog.setModal(True)  # 他のウィンドウの操作をブロック
        self.progressDialog.show()
        QApplication.processEvents()  # UIを更新
        
        csv_path = f"exported/{video_file_path.split('/')[-1].split('.')[-2]}.csv"
        csv_path2 = f"exported/{video_file_path2.split('/')[-1].split('.')[-2]}.csv"
        
        target_fps = self.player2.get_video_fps()
        
        output_video_file_name = self.output_video_file_name_input.text()
        color1 = self.player1.getSelectedColor()
        color2 = self.player2.getSelectedColor()
        
        overlap_frame_base = self.player1.getOverlapFrame()
        overlap_frame_target = self.player2.getOverlapFrame()
        
        if overlap_frame_base == None or overlap_frame_target == None:
            self.errorDialog = QErrorMessage(self)
            self.errorDialog.setWindowTitle("Error")
            self.errorDialog.showMessage("Overlap Frame is invalid.")
            self.errorDialog.show()
            self.progressDialog.close()
            return
        
        overlap_body_part_base = self.player1.overlap_body_part_combo_box.currentText()
        overlap_body_part_target = self.player2.overlap_body_part_combo_box.currentText()

        generate_video_with_bone.generate_download_video(video_file_path,csv_path, csv_path2, target_fps, overlap_frame_base, overlap_frame_target, overlap_body_part_base, overlap_body_part_target, color1, color2, output_video_file_name)

        # プログレスダイアログを閉じる
        self.progressDialog.close()

class SingleVideoPlayer(QWidget):
    def __init__(self, parent=None, isBase=False):
        super().__init__(parent)

        # レイアウトの設定
        self.layout = QVBoxLayout(self)

        self.topLayout = QHBoxLayout()

        # ボタンの設定
        if isBase:
            self.openButton = QPushButton(f" Select Base Video", self)
        else:
            self.openButton = QPushButton(f" Select Overlap Video", self)
            
        self.openButton.clicked.connect(self.openFile)
        self.openButton.setFixedSize(
            self.openButton.sizeHint())  # ボタンの横幅を文字がちょうど収まる程度に設定
        self.topLayout.addWidget(self.openButton)

        # 動画情報のラベル
        self.infoLabel = QLabel(self)
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.topLayout.addWidget(self.infoLabel)

        self.layout.addLayout(self.topLayout)

        # ビデオ表示の設定
        self.graphicsView = QGraphicsView(self)
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.layout.addWidget(self.graphicsView)

        # タイマーの設定
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)

        # コントロールボタンのレイアウト
        self.controlLayout = QHBoxLayout()

        # 再生ボタンの設定
        self.playButton = QPushButton("▶", self)  # 再生アイコン
        self.playButton.clicked.connect(self.startPlay)
        self.controlLayout.addWidget(self.playButton)

        # 続きから再生ボタンの設定
        self.resumeButton = QPushButton("⏯", self)  # 続きから再生アイコン
        self.resumeButton.clicked.connect(self.resumePlay)
        self.controlLayout.addWidget(self.resumeButton)

        # 停止ボタンの設定
        self.stopButton = QPushButton("⏹", self)  # 停止アイコン
        self.stopButton.clicked.connect(self.stopPlay)
        self.controlLayout.addWidget(self.stopButton)

        self.layout.addLayout(self.controlLayout)

        # 再生位置を示すスライダーバーの追加
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.setPosition)
        self.layout.addWidget(self.slider)
        
        self.setting_layout = QHBoxLayout()
        
        self.setting_layout.addStretch(1)
        
        # 文字列を表示
        self.overlap_frame_input_label = QLabel("Overlap Frame", self)
        self.setting_layout.addWidget(self.overlap_frame_input_label)
        
        # 文字列を入力できる入力欄の設定
        self.overlap_frame_input = QLineEdit(self)
        self.overlap_frame_input.setFixedWidth(80)
        self.overlap_frame_input.setStyleSheet("QLineEdit { border-radius: 5px; }")
        self.setting_layout.addWidget(self.overlap_frame_input)
        
        # 文字列を表示
        self.overlap_body_part_label = QLabel("Overlap Body Part", self)
        self.setting_layout.addWidget(self.overlap_body_part_label)
        
        # 重ねる部位を選択できるプルダウンの設定
        self.overlap_body_part_combo_box = QComboBox(self)
        self.overlap_body_part_combo_box.addItems(generate_video_with_bone.body_parts_mapping.keys())
        self.overlap_body_part_combo_box.setFixedWidth(120)
        self.setting_layout.addWidget(self.overlap_body_part_combo_box)
        
        # 文字列を表示
        self.output_video_file_name_label = QLabel("Bone Color", self)
        self.setting_layout.addWidget(self.output_video_file_name_label)

        # 色を選択できるプルダウンの設定
        self.colorComboBox = QComboBox(self)
        self.colorComboBox.addItems(["red", "blue", "green", "yellow", "white", "black"])
        self.colorComboBox.setFixedWidth(100)
        self.setting_layout.addWidget(self.colorComboBox)
        
        self.layout.addLayout(self.setting_layout)

        # メンバ変数の初期化
        self.cap = None
        self.currentFrame = None
        self.fps = 0
        self.totalFrames = 0
        self.video_file_path = ""

    def openFile(self):
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
        generated_video_path = generate_video_with_bone.generate_download_video(self.video_file_path, csv_path, "", 60, 0, 0, "waistCenter", "waistCenter", self.colorComboBox.currentText(), "blue", "")
        
        if generated_video_path:
            self.cap = cv2.VideoCapture(generated_video_path)
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.totalFrames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.setRange(0, self.totalFrames)
            self.timer.start(int(1000 / self.fps))
            
        # プログレスダイアログを閉じる
        self.progressDialog.close()

    def updateFrame(self):
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
            self.graphicsView.setScene(self.scene)
            self.graphicsView.fitInView(
                self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
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
                qImg = QImage(frame.data, width, height, bytesPerLine,
                              QImage.Format.Format_RGB888).rgbSwapped()
                pixmap = QPixmap.fromImage(qImg)
                self.scene.clear()
                self.scene.addPixmap(pixmap)
                self.graphicsView.setScene(self.scene)
                self.graphicsView.fitInView(
                    self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
                self.updateInfoLabel()
            else:
                self.timer.stop()

    def updateInfoLabel(self):
        currentFrameNum = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.infoLabel.setText(
            f"FPS: {self.fps} | Total Frames: {self.totalFrames} | Current Frame: {currentFrameNum}")
        
    def get_video_file_path(self):
        return self.video_file_path
    
    def get_current_frame(self):
        currentFrameNum = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        return currentFrameNum
    
    def get_video_fps(self):
        return self.fps
    
    def getOverlapFrame(self):
        try:
            overlap_frame = int(self.overlap_frame_input.text())
            if 0 <= overlap_frame and overlap_frame <= self.totalFrames:
                return overlap_frame
            else:
                return None
        except:
            return None
    
    def getSelectedColor(self):
        return self.colorComboBox.currentText()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
