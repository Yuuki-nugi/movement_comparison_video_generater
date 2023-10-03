import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget,QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSlider, QLabel, QSizePolicy, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QLineEdit, QComboBox
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QProgressDialog, QErrorMessage



class GeneratedVideoPlayer(QWidget):
    def __init__(self, video_file_path):
        super().__init__()

        # メインレイアウトの設定
        self.layout = QVBoxLayout(self)

        # 1つ目の動画プレイヤーの設定
        self.player1 = SingleVideoPlayer(self, video_file_path)
        self.layout.addWidget(self.player1)
        
        # ウィンドウの設定
        self.setLayout(self.layout)
        self.setWindowTitle("Movement Comparison Video Generator")
        self.resize(1600, 600)

   
class SingleVideoPlayer(QWidget):
    def __init__(self, parent=None, video_file_path=None):
        super().__init__(parent)
        
        # メンバ変数の初期化
        self.cap = None
        self.currentFrame = None
        self.fps = 0
        self.totalFrames = 0

        # レイアウトの設定
        self.layout = QVBoxLayout(self)

        self.topLayout = QHBoxLayout()

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
        
        # プログレスダイアログの設定
        self.progressDialog = QProgressDialog("Processing...", None, 0, 0, self)
        self.progressDialog.setWindowTitle("Please Wait")
        self.progressDialog.setModal(True)  # 他のウィンドウの操作をブロック
        self.progressDialog.show()
        QApplication.processEvents()  # UIを更新
            
        if video_file_path:
            self.cap = cv2.VideoCapture(video_file_path)
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.totalFrames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.setRange(0, self.totalFrames)
            
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.updateFrame)
            self.timer.start(int(1000 / self.fps))
        else:
            error_dialog = QErrorMessage(self)
            error_dialog.showMessage('Not found video file.')
            error_dialog.exec()
            return
            
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
