import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSlider
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, Qt


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # レイアウトの設定
        self.layout = QVBoxLayout(self)

        # ボタンの設定
        self.openButton = QPushButton("動画選択", self)
        self.openButton.clicked.connect(self.openFile)
        self.layout.addWidget(self.openButton)

        # ビデオウィジェットの設定
        self.videoWidget = QVideoWidget(self)
        self.layout.addWidget(self.videoWidget)

        # メディアプレイヤーの設定
        self.mediaPlayer = QMediaPlayer(self)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

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
        self.mediaPlayer.positionChanged.connect(self.updatePosition)
        self.mediaPlayer.durationChanged.connect(self.updateDuration)
        self.layout.addWidget(self.slider)

        # 閉じるボタンの設定
        self.closeButton = QPushButton("閉じる", self)
        self.closeButton.clicked.connect(self.close)
        self.layout.addWidget(self.closeButton)

        # ウィンドウの設定
        self.setLayout(self.layout)
        self.setWindowTitle("動画プレイヤー")
        self.resize(800, 600)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open Movie", "", "All Files (*);;Movie Files (*.mp4 *.avi)")
        if fileName != '':
            self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
            self.mediaPlayer.play()

    def startPlay(self):
        self.mediaPlayer.setPosition(0)
        self.mediaPlayer.play()

    def resumePlay(self):
        self.mediaPlayer.play()

    def stopPlay(self):
        self.mediaPlayer.pause()

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def updatePosition(self, position):
        self.slider.setValue(position)

    def updateDuration(self, duration):
        self.slider.setRange(0, duration)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
