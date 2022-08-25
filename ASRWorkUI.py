# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 23:16:43 2021

@author: muxia
"""

import os
import sys
import librosa
from pathlib import Path
import time
from collections import defaultdict
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QPushButton, QHBoxLayout, QMainWindow, QWidget,
                             QVBoxLayout, QLineEdit, QSpacerItem, QLabel, QTextEdit,
                             QComboBox, QSizePolicy, QFileDialog, QMessageBox, QCheckBox, QLabel)

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPalette, QPixmap, QBrush
from playsound import playsound
import time
import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
# 使用 matplotlib中的FigureCanvas (在使用 Qt5 Backends中 FigureCanvas继承自QtWidgets.QWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
import sqlite3
matplotlib.use('Qt5Agg')

class QuitApplication(QMainWindow):
    def __init__(self):
        super(QuitApplication, self).__init__()
        self.setWindowTitle("AudioEventClassifier")

        self.cwd = os.getcwd()


        self.resize(1200, 800)
        # self.setFixedSize(1200, 800)

        ## 整体布局
        self.globalVLayout = QVBoxLayout()

        ## 字体
        font_btn = QFont()
        font_btn.setFamily("Consolas")
        font_btn.setBold(True)

        font_le = QFont()
        font_le.setFamily("Consolas")

        font_lbl = QFont()
        font_lbl.setFamily("Consolas")
        font_lbl.setBold(True)

        self.status = self.statusBar()
        self.status.setFont(font_le)
        self.status.showMessage("准备就绪...")

        ## 输入、输出、字符集和忽略字符的spacer

        sp_readpath_left = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        sp_readpath_mid = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        sp_readpath_right = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        ## 输入数据的布局
        self.inputHLayout = QHBoxLayout()

        self.btn_text = QPushButton("输入文本路径")
        self.le_textfile = QLineEdit()

        self.btn_text.clicked.connect(self.onClickChooseTextFile)
        self.btn_text.setFont(font_btn)
        self.le_textfile.setFont(font_le)

        # self.inputHLayout.addItem(sp_readpath_left)
        self.inputHLayout.addWidget(self.btn_text)
        # self.inputHLayout.addItem(sp_readpath_mid)
        self.inputHLayout.addWidget(self.le_textfile)
        # self.inputHLayout.addItem(sp_readpath_right)



        ##  输入语音布局
        self.AudioHLayout = QHBoxLayout()

        self.btn_audio = QPushButton("输入音频文件夹: ")
        self.le_audio = QLineEdit()

        self.lbl_progress = QLabel()

        self.btn_audio.clicked.connect(self.onClickAudioDir)
        self.btn_audio.setFont(font_btn)
        self.le_audio.setFont(font_le)

        self.AudioHLayout.addWidget(self.btn_audio)
        self.AudioHLayout.addWidget(self.le_audio)
        self.AudioHLayout.addWidget(self.lbl_progress)


        ## 原始结果的布局
        self.refHLayout = QHBoxLayout()

        self.lbl_ref = QLabel("Label")
        self.le_ref = QLineEdit()
        self.le_ref.setFont(font_le)

        self.refHLayout.addWidget(self.lbl_ref)
        self.refHLayout.addWidget(self.le_ref)


        ## 识别结果的布局
        self.recHLayout = QHBoxLayout()

        self.lbl_rec = QLabel("AsrCERENCE")
        self.le_rec = QLineEdit()
        self.le_rec.setFont(font_le)

        self.recHLayout.addWidget(self.lbl_rec)
        self.recHLayout.addWidget(self.le_rec)

        ## 大屏幕布局
        self.contentHLayout = QHBoxLayout()
        self.te_content = QTextEdit()
        self.te_content.setFont(font_le)
        self.te_content.setReadOnly(True)
        self.contentHLayout.addWidget(self.te_content)

        ## 检查text或者textgrid格式按钮布局
        self.RunHLayout = QHBoxLayout()

        self.btn_run = QPushButton("接受")
        self.btn_run.setFont(font_le)
        self.btn_run.setMinimumSize(20, 20)
        self.btn_clear = QPushButton("不接受")
        self.btn_clear.setFont(font_le)
        self.btn_clear.setMinimumSize(20, 20)
        self.btn_close = QPushButton("关闭")
        self.btn_close.setFont(font_le)
        self.btn_close.setMinimumSize(20, 20)

        self.btn_run.clicked.connect(self.onClickStart)
        self.btn_close.clicked.connect(self.close)
        self.btn_clear.clicked.connect(self.onClickClear)

        self.RunHLayout.addItem(sp_readpath_left)
        self.RunHLayout.addWidget(self.btn_run)
        self.RunHLayout.addItem(sp_readpath_mid)
        self.RunHLayout.addWidget(self.btn_clear)
        self.RunHLayout.addItem(sp_readpath_mid)
        self.RunHLayout.addWidget(self.btn_close)
        self.RunHLayout.addItem(sp_readpath_right)



        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.ShowHLayout =QHBoxLayout()
        self.ShowHLayout.addWidget(self.canvas)

        ## 将子布局全部添加到整体布局
        self.globalVLayout.addLayout(self.ShowHLayout)
        self.globalVLayout.addLayout(self.refHLayout)
        self.globalVLayout.addLayout(self.recHLayout)
        self.globalVLayout.addLayout(self.inputHLayout)
        self.globalVLayout.addLayout(self.AudioHLayout)
        self.globalVLayout.addLayout(self.contentHLayout)
        self.globalVLayout.addLayout(self.RunHLayout)

        self.audio2text = None
        self.audio2path = None
        self.audio_name = None
        self.audio_index = 0

        mainFrame = QWidget()
        mainFrame.setLayout(self.globalVLayout)
        self.setCentralWidget(mainFrame)

        self.db_path = "database/annotation.db"
        self.conn = None
        self.cur = None
        self.results = {}

        if not os.path.exists(self.db_path):
            self.createDB()
        else:
            self.loadExistedData()
        print(self.results)

    def createDB(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        # 建立一个表
        information = '''CREATE TABLE annotation
        (audio_name TEXT,
         audio_path TEXT,
         is_accept TEXT,
         time TEXT,
         notation TEXT,
         AsrCERENCE TEXT,
         Label TEXT
        )
        '''
        self.cur.execute(information)

    def plot_(self, audio_path):
        plt.cla()
        y, sr = librosa.load(audio_path)
        ax = plt.plot(y)
        self.canvas.draw()


    def onClickChooseTextFile(self):
        text_file, filetype = QFileDialog.getOpenFileName(self, "选择文件", self.cwd,
                                              "Text Files(*.txt)")
        self.le_textfile.setText(text_file)
        self.te_content.append(f"Reading Text File from {text_file}...")
        self.read_thread = ReadTextFileThread(text_file)

        self.read_thread.audio_info.connect(self.getText)
        self.read_thread.start()

        return text_file

    def loadExistedData(self):
        ## 加载已经存在的db文件
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        cmd = """SELECT * FROM annotation"""
        self.cur.execute(cmd)
        history_data = self.cur.fetchall()
        print(history_data)
        for ele in history_data:
            wavname, wavpath, is_accept, do_time, notation, rec_text, ref_text = ele
            if wavname in self.results.keys():
                prev_time = self.results[wavname]["time"]
                if do_time > prev_time:
                    self.results[wavname] = {
                            "audio_name": wavname,
                            "audio_path": wavpath,
                            "is_accept": is_accept,
                            "time": do_time,
                            "notation": notation,
                            "AsrCERENCE": rec_text,
                            "Label": ref_text
                            }
            else:
                self.results[wavname] = {
                        "audio_name": wavname,
                        "audio_path": wavpath,
                        "is_accept": is_accept,
                        "time": do_time,
                        "notation": notation,
                        "AsrCERENCE": rec_text,
                        "Label": ref_text
                        }
        print(self.results)

    def lastOne(self):
        ## 回退到上一条
        pass

    def selectByIndex(self, index):
        ## 显示某一条的标注结果
        pass

    def exportDB(self):
        ## 点击导出按钮的时候导出这个结果
        pass

    def getText(self, audio2text):
        self.audio2text = audio2text
        for ele in self.audio2text:
            if ele[0] in self.results.keys():
                self.audio_index += 1
        if self.audio_index == len(self.audio2text):
            self.audio_index -= 1
        self.audio_name = self.audio2text[self.audio_index][0]
        self.le_rec.setText(self.audio2text[self.audio_index][1])
        self.le_ref.setText(self.audio2text[self.audio_index][2])
        self.audio_index += 1
        self.lbl_progress.setText(f"{self.audio_index}/{len(self.audio2text)}")


    def onClickAudioDir(self):
        audio_dir = QFileDialog.getExistingDirectory(self, "选取文件夹")
        self.le_audio.setText(audio_dir)

        self.te_content.append(f"Find all audio files from {audio_dir}...")
        self.find_audios = FindAudioThread(audio_dir)
        self.find_audios.audio_info.connect(self.getWavFiles)
        self.find_audios.start()
        return audio_dir


    def getWavFiles(self, audio2path):
        self.audio2path = audio2path
        if self.audio_name:
            audio_path = self.audio2path[self.audio_name]
            self.plot_(audio_path)
            self.play_thread = PlayThread(audio_path)
            self.play_thread.start()



    def onClickClear(self):
        wav_dir = self.le_audio.text()
        if not os.path.exists(wav_dir):
            QMessageBox.warning(self, 'ERROR', "语音不存在", QMessageBox.Yes, QMessageBox.Yes)
            return
        textfile = self.le_textfile.text()
        if not os.path.exists(textfile):
            QMessageBox.warning(self, 'ERROR', "文本不存在", QMessageBox.Yes, QMessageBox.Yes)
            return
        self.lbl_progress.setText(f"{self.audio_index}/{len(self.audio2text)}")
        if self.audio_index == len(self.audio2text):
            return
        rec_text = self.le_rec.text()
        ref_text = self.le_ref.text()
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d-%H-%M-%S")
        anno_result = """INSERT INTO annotation VALUES(?,?,?,?,?,?, ?)"""
        value = (self.audio2text[self.audio_index - 1][0], self.audio2path[self.audio_name], 'N', now_str, '', rec_text, ref_text)
        self.cur.execute(anno_result, value)
        self.conn.commit()
        self.audio_name = self.audio2text[self.audio_index][0]
        self.le_rec.setText(self.audio2text[self.audio_index][1])
        self.le_ref.setText(self.audio2text[self.audio_index][2])

        audio_path = self.audio2path[self.audio_name]
        self.plot_(audio_path)
        self.play_thread = PlayThread(audio_path)
        self.play_thread.start()
        self.audio_index += 1

    def onClickStart(self):
        wav_dir = self.le_audio.text()
        print(wav_dir)
        if not os.path.exists(wav_dir):
            QMessageBox.warning(self, 'ERROR', "语音不存在", QMessageBox.Yes, QMessageBox.Yes)
            return
        textfile = self.le_textfile.text()
        if not os.path.exists(textfile):
            QMessageBox.warning(self, 'ERROR', "文本不存在", QMessageBox.Yes, QMessageBox.Yes)
            return
        if self.audio_name in self.results.keys():
            self.audio_index += 1
            return
        self.lbl_progress.setText(f"{self.audio_index}/{len(self.audio2text)}")
        if self.audio_index == len(self.audio2text):
            return
        rec_text = self.le_rec.text()
        ref_text = self.le_ref.text()
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d-%H-%M-%S")
        anno_result = """INSERT INTO annotation VALUES(?,?,?,?,?,?, ?)"""
        value = (self.audio2text[self.audio_index - 1][0], self.audio2path[self.audio_name], 'Y', now_str, '', rec_text, ref_text)
        print(anno_result)
        self.cur.execute(anno_result, value)
        self.conn.commit()
        self.audio_name = self.audio2text[self.audio_index][0]
        self.le_rec.setText(self.audio2text[self.audio_index][1])
        self.le_ref.setText(self.audio2text[self.audio_index][2])

        audio_path = self.audio2path[self.audio_name]
        self.plot_(audio_path)
        self.play_thread = PlayThread(audio_path)
        self.play_thread.start()
        self.audio_index += 1


    def onClickPlay(self):
        wav_path = self.le_audio.text()
        if not os.path.exists(wav_path):
            QMessageBox.warning(self, 'ERROR', "语音不存在", QMessageBox.Yes, QMessageBox.Yes)
            return
        self.play_thread = PlayThread(wav_path)
        self.play_thread.start()

    def setDone(self):
        self.setEnableTrue()


    def HaveLoadModel(self):
        self.ModelLoaded = True
        self.te_content.append("Loading Model SUCCESS!")

    def show_info(self, msgs):
        self.te_content.append(msgs)

    def setStaus(self, content):
        self.status.showMessage(content)

class PlayThread(QThread):
    done_signal = pyqtSignal()
    def __init__(self, wav_path):
        super(PlayThread, self).__init__()
        self.wavp = wav_path

    def run(self):
        playsound(self.wavp)



class ReadTextFileThread(QThread):
    audio_info = pyqtSignal(list)
    def __init__(self, text_file):
        super(ReadTextFileThread, self).__init__()
        self.text_file = text_file

    def run(self):
        contents = open(self.text_file, encoding="utf-8").readlines()
        audio2text = []
        for line in contents[1:]:
            audio_name, rec_result, ref_result = line.strip().split("\t")
            audio_list = [audio_name, rec_result, ref_result]
            audio2text.append(audio_list)

        self.audio_info.emit(audio2text)


class FindAudioThread(QThread):
    audio_info = pyqtSignal(dict)
    def __init__(self, audio_dir):
        super(FindAudioThread, self).__init__()
        self.audio_dir = audio_dir

    def run(self):
        audio2path = {}
        audio_files = Path(self.audio_dir).rglob("*.wav")
        for audio_file in audio_files:
            audio_file = str(audio_file)
            audio_name = os.path.basename(audio_file)
            audio2path[audio_name] = audio_file

        self.audio_info.emit(audio2path)


if __name__=="__main__":
    app = QApplication(sys.argv)
    w = QuitApplication()
    w.show()
    sys.exit(app.exec_())