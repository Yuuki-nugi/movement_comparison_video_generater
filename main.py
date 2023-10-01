import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSlider, QLabel, QSizePolicy, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QBrush, QLinearGradient
from PyQt6.QtCore import QUrl, Qt, QTimer, QPropertyAnimation, pyqtProperty


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # メインレイアウトの設定
        self.layout = QVBoxLayout(self)

        # 2つの動画プレイヤーのレイアウト
        self.playersLayout = QHBoxLayout()

        # 1つ目の動画プレイヤーの設定
        self.player1 = SingleVideoPlayer(self)
        self.playersLayout.addWidget(self.player1)

        # 2つ目の動画プレイヤーの設定
        self.player2 = SingleVideoPlayer(self)
        self.playersLayout.addWidget(self.player2)

        self.layout.addLayout(self.playersLayout)

        self.functionsLayout = QHBoxLayout()

        # 閉じるボタンの設定
        self.closeButton = QPushButton(" 閉じる ", self)
        self.closeButton.setFixedSize(
            self.closeButton.sizeHint())  # ボタンの横幅を文字がちょうど収まる程度に設定
        self.closeButton.clicked.connect(self.close)
        self.functionsLayout.addWidget(self.closeButton)

        # 動画生成ボタンの設定
        self.generateButton = QPushButton(" ボーン合成動画の生成 ", self)
        self.generateButton.clicked.connect(self.generateVideo)
        self.generateButton.setFixedSize(
            self.generateButton.sizeHint())  # ボタンの横幅を文字がちょうど収まる程度に設定
        self.functionsLayout.addWidget(self.generateButton)

        self.layout.addLayout(self.functionsLayout)

        # ウィンドウの設定
        self.setLayout(self.layout)
        self.setWindowTitle("動画プレイヤー")
        self.resize(1600, 600)

    def generateVideo(self):
        # 空のメソッド
        pass


class SingleVideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # レイアウトの設定
        self.layout = QVBoxLayout(self)

        self.topLayout = QHBoxLayout()

        # ボタンの設定
        self.openButton = QPushButton(" 動画選択 ", self)
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

        # メンバ変数の初期化
        self.cap = None
        self.currentFrame = None
        self.fps = 0

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open Movie", "", "All Files (*);;Movie Files (*.mp4 *.avi)")
        if fileName:
            self.cap = cv2.VideoCapture(fileName)
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.totalFrames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.setRange(0, self.totalFrames)
            self.timer.start(int(1000 / self.fps))

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
