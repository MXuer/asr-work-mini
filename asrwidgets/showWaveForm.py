# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 18:13:18 2022

@author: muxia
"""

import os
import logging

import librosa
import matplotlib
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (QApplication, QPushButton, QHBoxLayout, QMainWindow, QWidget,
                             QVBoxLayout, QLineEdit, QTextEdit, QTextEdit,
                             QComboBox, QFileDialog, QMessageBox,
                             QGridLayout, QLabel)


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class QShowWavform(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self):

        self.widget = QWidget()
        self.layout = QGridLayout()
        self.widget.setLayout(self.layout)

        self.figure = plt.figure()
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
        ax = plt.axes()
        ax.set_facecolor('black')
        self.canvas = FigureCanvas(self.figure)

        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def add_wavform(self, wav_path: str) -> None:
        plt.cla()
        y, sr = librosa.load(wav_path)
        plt.plot(y, color='navajowhite')
        self.canvas.draw()

