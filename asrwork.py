# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 23:16:43 2021

@author: muxia
"""

import os
import sys
from datetime import datetime

import logging

from PyQt5.QtWidgets import (QApplication, QPushButton, QHBoxLayout, QMainWindow, QWidget,
                             QVBoxLayout, QLineEdit, QComboBox, QFileDialog, QMessageBox,
                             QGridLayout, QLabel)

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont

import qdarkstyle

import sqlite3

# 导入所有的自定义的QWidget
from asrwidgets.showWaveForm import QShowWavform
from asrwidgets.checkableCombox import CheckableComboBox
from asrwork_threads import ReadTextFileThread, FindAudioThread, PlayAndStopThread

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
                    datefmt='%Y-%m-%d %A %H:%M:%S')
logger = logging.getLogger()


class QuitApplication(QMainWindow):
    signal = pyqtSignal()

    def __init__(self):
        super(QuitApplication, self).__init__()
        self.setWindowTitle("ASR_NLU_WORK")

        self.resize(1000, 600)
        # self.setFixedSize(1200, 800)

        # 整体布局
        self.globalVLayout = QVBoxLayout()

        # 字体
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

        self.audio2text = None
        self.audio2path = None
        self.audio_name = None
        self.audio_index = 0

        # 设定主界面的layout
        self.main_widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        # 上下两个layout，一个用来放语音的播放界面，另外一个用来人工的操作以及tag什么都
        self.up_widget = QWidget()
        self.up_layout = QGridLayout()
        self.up_widget.setLayout(self.up_layout)

        self.down_widget = QWidget()
        self.down_layout = QGridLayout()
        self.down_widget.setLayout(self.down_layout)

        # 把这两个qwidget放到main widget里面去
        self.main_layout.addWidget(self.up_widget, 0, 0, 1, 6)
        self.main_layout.addWidget(self.down_widget, 1, 0, 4, 6)

        # 把语音的波形界面添加到up_widget中
        self.show_wavform_widget = QShowWavform()
        self.up_layout.addWidget(self.show_wavform_widget)

        # 右边分两层，一个是显示文本，二个是显示选择音频和文本文件的路径
        self.text_widget = QWidget()
        self.text_layout = QHBoxLayout()
        self.text_widget.setLayout(self.text_layout)

        self.lbl_text_widget = QWidget()
        self.lbl_text_layout = QVBoxLayout()
        self.lbl_text_widget.setLayout(self.lbl_text_layout)

        self.le_text_widget = QWidget()
        self.le_text_layout = QVBoxLayout()
        self.le_text_widget.setLayout(self.le_text_layout)

        self.text_layout.addWidget(self.lbl_text_widget)
        self.text_layout.addWidget(self.le_text_widget)

        # 添加文本操作的label
        self.lbl_ref = QLabel("Label")
        self.lbl_ref.setFont(font_le)
        self.lbl_rec = QLabel("AsrCERENCE")
        self.lbl_rec.setFont(font_le)
        self.lbl_cerence = QLabel("CERENCE")
        self.lbl_cerence.setFont(font_le)
        self.lbl_comments = QLabel("COMMETS")
        self.lbl_comments.setFont(font_le)
        self.lbl_text_layout.addWidget(self.lbl_ref)
        self.lbl_text_layout.addWidget(self.lbl_rec)
        self.lbl_text_layout.addWidget(self.lbl_cerence)
        self.lbl_text_layout.addWidget(self.lbl_comments)

        # comments的布局
        self.comments_widget = QWidget()
        self.comments_layout = QHBoxLayout()
        self.comments_widget.setLayout(self.comments_layout)

        self.le_comments = QLineEdit()
        self.le_comments.setFont(font_le)
        self.cbox_comments = CheckableComboBox()

        # 读取comments文件
        self.cbox_comments.addItem("全选")
        comment_file = os.path.join(os.getcwd(), "comments", "comments.txt")
        for line in open(comment_file, encoding='utf-8-sig'):
            comment = line.strip()
            self.cbox_comments.addItem(comment)
        self.cbox_comments.currentIndexChanged.connect(self.showInCommentsLineEdit)

        self.comments_layout.addWidget(self.le_comments)
        self.comments_layout.addWidget(self.cbox_comments)

        # 添加文本操作的line edit
        self.le_ref = QLineEdit()
        self.le_ref.setFont(font_le)
        self.le_rec = QLineEdit()
        self.le_rec.setFont(font_le)
        self.le_1 = QLineEdit()
        self.le_1.setFont(font_le)
        self.le_text_layout.addWidget(self.le_ref)
        self.le_text_layout.addWidget(self.le_rec)
        self.le_text_layout.addWidget(self.le_1)
        self.le_text_layout.addWidget(self.comments_widget)

        # 添加打开文件和上一句下一句的组件
        self.op_widget = QWidget()
        self.op_layout = QHBoxLayout()
        self.op_widget.setLayout(self.op_layout)

        # 左边两个button
        self.op_btn_widget = QWidget()
        self.op_btn_layout = QVBoxLayout()
        self.op_btn_widget.setLayout(self.op_btn_layout)

        self.btn_text = QPushButton("script")
        self.btn_text.clicked.connect(self.onClickChooseTextFile)
        self.btn_text.setFont(font_btn)

        self.btn_audio = QPushButton("wave")
        self.btn_audio.clicked.connect(self.onClickAudioDir)
        self.btn_audio.setFont(font_btn)

        self.op_btn_layout.addWidget(self.btn_text)
        self.op_btn_layout.addWidget(self.btn_audio)

        # 中间的路径line edit
        self.op_le_widget = QWidget()
        self.op_le_layout = QVBoxLayout()
        self.op_le_widget.setLayout(self.op_le_layout)

        self.le_audio = QLineEdit()
        self.le_audio.setFont(font_le)
        self.le_textfile = QLineEdit()
        self.le_textfile.setFont(font_le)

        self.op_le_layout.addWidget(self.le_textfile)
        self.op_le_layout.addWidget(self.le_audio)

        # 中间的上一句下一句btn
        self.op_choose_btn_widget = QWidget()
        self.op_choose_btn_layout = QVBoxLayout()
        self.op_choose_btn_widget.setLayout(self.op_choose_btn_layout)

        self.btn_prev = QPushButton("上一句")
        self.btn_prev.clicked.connect(self.onClickPrev)
        self.btn_prev.setFont(font_btn)

        self.btn_next = QPushButton("下一句")
        self.btn_next.clicked.connect(self.onClickNext)
        self.btn_next.setFont(font_btn)

        self.op_choose_btn_layout.addWidget(self.btn_prev)
        self.op_choose_btn_layout.addWidget(self.btn_next)

        self.cb_choose_widget = QWidget()
        self.cb_layout = QGridLayout()
        self.cb_choose_widget.setLayout(self.cb_layout)

        self.cb_choose = QComboBox()

        self.cb_layout.addWidget(self.cb_choose)

        self.op_layout.addWidget(self.op_btn_widget)
        self.op_layout.addWidget(self.op_le_widget)
        self.op_layout.addWidget(self.op_choose_btn_widget)
        self.op_layout.addWidget(self.cb_choose_widget)

        self.run_widget = QWidget()
        self.run_layout = QHBoxLayout()
        self.run_widget.setLayout(self.run_layout)

        self.btn_run = QPushButton("接受")
        self.btn_run.setFont(font_le)
        self.btn_run.setMinimumSize(20, 20)
        self.btn_clear = QPushButton("不接受")
        self.btn_clear.setFont(font_le)
        self.btn_clear.setMinimumSize(20, 20)
        self.btn_export = QPushButton("导出")
        self.btn_export.setFont(font_le)
        self.btn_export.setMinimumSize(20, 20)

        self.btn_run.clicked.connect(self.onClickStart)
        self.btn_export.clicked.connect(self.export_results)
        self.btn_clear.clicked.connect(self.onClickClear)

        self.run_layout.addWidget(self.btn_run)
        self.run_layout.addWidget(self.btn_clear)
        self.run_layout.addWidget(self.btn_export)

        self.down_layout.addWidget(self.text_widget)
        self.down_layout.addWidget(self.op_widget)
        self.down_layout.addWidget(self.run_widget)

        self.setCentralWidget(self.main_widget)

        self.db_path = "database/annotation.db"
        self.conn = None
        self.cur = None
        self.results = {}

        if not os.path.exists(self.db_path):
            self.createDB()
        else:
            self.loadExistedData()

    def createDB(self) -> None:
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

    def export_results(self) -> None:
        if not self.results:
            QMessageBox.warning(self, 'ERROR', "没有可导出的结果", QMessageBox.Yes, QMessageBox.Yes)
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d-%H-%M-%S")
        result_dir = os.path.join("results", now_str)
        os.makedirs(result_dir, exist_ok=True)
        result_file = os.path.join(result_dir, "results.txt")
        with open(result_file, 'w', encoding='utf-8') as f:
            #TODO 改变result的存储结构，现在太麻烦了。
            for wavname, annote_info in self.results.items():
                logger.info(f"Write with {wavname}.")
                f.write("\t".join(list(annote_info.values())) + "\n")
        QMessageBox.information(self, 'DONE', "导出成功！", QMessageBox.Yes)

    def onClickChooseTextFile(self) -> str:
        text_file, filetype = QFileDialog.getOpenFileName(self, "选择文件", "", "Text Files(*.txt)")
        self.le_textfile.setText(text_file)
        self.read_thread = ReadTextFileThread(text_file)

        self.read_thread.audio_info.connect(self.getText)
        self.read_thread.start()

        return text_file

    def loadExistedData(self) -> None:
        """
        加载已经存在的db文件
        :return:
        """
        logger.info("Loading existed DB file.")
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        cmd = """SELECT * FROM annotation"""
        self.cur.execute(cmd)
        history_data = self.cur.fetchall()
        for ele in history_data:
            logger.info(f"Loading {ele}.")
            wavname, wavpath, is_accept, do_time, notation, rec_text, ref_text = ele
            if wavname in self.results.keys():
                prev_time = self.results[wavname]["time"]
                if do_time > prev_time:
                    self.results[wavname] = {
                        "audio_name": wavname,
                        "audio_path": wavpath,
                        "is_accept": is_accept,
                        "time": do_time,
                        "comments": notation,
                        "AsrCERENCE": rec_text,
                        "Label": ref_text
                    }
            else:
                self.results[wavname] = {
                    "audio_name": wavname,
                    "audio_path": wavpath,
                    "is_accept": is_accept,
                    "time": do_time,
                    "comments": notation,
                    "AsrCERENCE": rec_text,
                    "Label": ref_text
                }
        logger.info(f"Number of history data is {len(self.results.keys())}")

    def showInCommentsLineEdit(self) -> None:
        logger.info("Show the checked comments in line edit.")
        checked_comments = self.cbox_comments.getCheckItem()
        logger.info(f"Current Chosen comments is {checked_comments}")
        if checked_comments:
            self.le_comments.setText(",".join(checked_comments))
        else:
            self.le_comments.setText("")

    def onClickPrev(self) -> None:
        logger.info(f"Prev index : {self.audio_index}.")
        self.signal.emit()
        self.audio_index -= 1
        if self.audio_index < 0:
            QMessageBox.warning(self, 'ERROR', "没有上一句了。", QMessageBox.Yes, QMessageBox.Yes)
            return
        self.cb_choose.setCurrentIndex(self.audio_index)

    def onClickNext(self) -> None:
        logger.info(f"Next index : {self.audio_index}.")

        if self.audio_index + 1 == len(self.audio2text):
            QMessageBox.warning(self, 'ERROR', "没有下一句了。", QMessageBox.Yes, QMessageBox.Yes)
            return

        self.signal.emit()
        self.audio_index += 1
        self.cb_choose.setCurrentIndex(self.audio_index)

    def showCurrentData(self, index: int) -> None:
        logger.info(f"Show the current chosen index : {index}.")
        self.cbox_comments.clear_all()
        self.audio_name = self.audio2text[index][0]
        self.le_rec.setText(self.audio2text[index][1])
        self.le_ref.setText(self.audio2text[index][2])
        audio_path = self.audio2path[self.audio_name]
        self.show_wavform_widget.add_wavform(audio_path)
        self.play_thread = PlayAndStopThread(audio_path)
        self.signal.connect(self.play_thread.accept)
        self.play_thread.start()

    def indexChange(self) -> None:
        logger.info("Index Changed. Set Index Combox to corresponding index.")
        self.signal.emit()
        self.audio_index = int(self.cb_choose.currentText()) - 1
        logger.info(f"Current Index is {self.audio_index}.")
        self.showCurrentData(self.audio_index)

    def getText(self, audio2text: str) -> None:
        self.audio2text = audio2text
        for ele in self.audio2text:
            if ele[0] in self.results.keys():
                print(f"{ele[0]} already been processed.")
                self.audio_index += 1
        if self.audio_index == len(self.audio2text):
            self.audio_index -= 1
        self.audio_name = self.audio2text[self.audio_index][0]
        self.le_rec.setText(self.audio2text[self.audio_index][1])
        self.le_ref.setText(self.audio2text[self.audio_index][2])

    def onClickAudioDir(self) -> str:
        audio_dir = QFileDialog.getExistingDirectory(self, "选取文件夹")
        self.le_audio.setText(audio_dir)

        if audio_dir:
            self.find_audios = FindAudioThread(audio_dir)
            self.find_audios.audio_info.connect(self.getWavFiles)
            self.find_audios.start()
        return audio_dir

    def getWavFiles(self, audio2path: str) -> None:
        logger.info("Set the Item.")
        self.audio2path = audio2path
        if self.audio_name:
            self.showCurrentData(self.audio_index)
            for index in range(1, len(self.audio2text) + 1):
                self.cb_choose.addItem(str(index))
        self.cb_choose.setCurrentIndex(self.audio_index)
        self.cb_choose.currentIndexChanged.connect(self.indexChange)


    def onClickClear(self) -> None:
        self.signal.emit()
        wav_dir = self.le_audio.text()
        if not os.path.exists(wav_dir):
            QMessageBox.warning(self, 'ERROR', "语音不存在", QMessageBox.Yes, QMessageBox.Yes)
            return
        textfile = self.le_textfile.text()
        if not os.path.exists(textfile):
            QMessageBox.warning(self, 'ERROR', "文本不存在", QMessageBox.Yes, QMessageBox.Yes)
            return
        if self.audio_index == len(self.audio2text):
            QMessageBox.warning(self, 'ERROR', "没有下一句了。", QMessageBox.Yes, QMessageBox.Yes)
            return
        rec_text = self.le_rec.text()
        ref_text = self.le_ref.text()
        comments = self.le_comments.text()
        if not comments:
            QMessageBox.warning(self, 'ERROR', "Comments不可以为空", QMessageBox.Yes, QMessageBox.Yes)
            return

        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d-%H-%M-%S")
        anno_result = """INSERT INTO annotation VALUES(?,?,?,?,?,?, ?)"""
        value = (self.audio2text[self.audio_index - 1][0],
                 self.audio2path[self.audio_name],
                 '不接受',
                 now_str,
                 comments,
                 rec_text,
                 ref_text)

        self.cur.execute(anno_result, value)
        self.conn.commit()
        self.cb_choose.setCurrentIndex(self.audio_index)
        self.le_comments.clear()
        self.audio_index += 1

    def update_results(self, value: tuple) -> None:
        self.results[wavname] = {
            "audio_name": value[0],
            "audio_path": value[1],
            "is_accept": value[2],
            "time": value[3],
            "comments": value[4],
            "AsrCERENCE": value[5],
            "Label": value[6]
        }


    def onClickStart(self) -> None:
        logger.info(f"Accept for {self.audio_index}. Current audio is {self.audio_name}.")
        self.signal.emit()
        wav_dir = self.le_audio.text()
        if not os.path.exists(wav_dir):
            QMessageBox.warning(self, 'ERROR', "语音不存在", QMessageBox.Yes, QMessageBox.Yes)
            return
        textfile = self.le_textfile.text()
        if not os.path.exists(textfile):
            QMessageBox.warning(self, 'ERROR', "文本不存在", QMessageBox.Yes, QMessageBox.Yes)
            return
        if self.audio_index == len(self.audio2text):
            QMessageBox.warning(self, 'ERROR', "没有下一句了。", QMessageBox.Yes, QMessageBox.Yes)
            return
        comments = self.le_comments.text()
        if not comments:
            QMessageBox.warning(self, 'ERROR', "Comments不可以为空", QMessageBox.Yes, QMessageBox.Yes)
            return
        rec_text = self.le_rec.text()
        ref_text = self.le_ref.text()
        logger.info(f"Cerence Text: {rec_text}.")
        logger.info(f"Labeled Text: {ref_text}.")
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d-%H-%M-%S")
        anno_result = """INSERT INTO annotation VALUES(?,?,?,?,?,?, ?)"""
        value = (self.audio2text[self.audio_index - 1][0],
                 self.audio2path[self.audio_name],
                 '接受',
                 now_str,
                 comments,
                 rec_text,
                 ref_text)
        self.cur.execute(anno_result, value)
        self.conn.commit()
        self.cb_choose.setCurrentIndex(self.audio_index)
        self.le_comments.clear()
        self.audio_index += 1

    def onClickPlay(self) -> None:
        wav_path = self.le_audio.text()
        if not os.path.exists(wav_path):
            QMessageBox.warning(self, 'ERROR', "语音不存在", QMessageBox.Yes, QMessageBox.Yes)
            return
        self.play_thread = PlayAndStopThread(wav_path)
        self.signal.connect(self.play_thread.accept)
        self.play_thread.start()

    def setDone(self) -> None:
        self.setEnableTrue()

    def setStaus(self, content: str) -> None:
        self.status.showMessage(content)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # # or in new API
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

    w = QuitApplication()
    w.show()
    sys.exit(app.exec_())
