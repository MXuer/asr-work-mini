# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 18:20:51 2022

@author: muxia
"""


import sys

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QMainWindow

from asrwidgets.showWaveForm import QShowWavform


WAV_PATH = "data/1b_10036.wav"

class TestQShowWavform(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.resize(1000, 600)

        self.main_widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        self.show_wavform_widget = QShowWavform()

        self.main_layout.addWidget(self.show_wavform_widget)
        self.test_add_wavform()
        self.setCentralWidget(self.main_widget)

    def test_add_wavform(self):
        self.show_wavform_widget.add_wavform(WAV_PATH)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TestQShowWavform()
    w.show()

    sys.exit(app.exec_())