import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
