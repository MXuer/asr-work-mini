# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 18:44:50 2022

@author: muxia
"""

import os
import wave
import logging

import pyaudio

from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal


class ReadTextFileThread(QThread):
    audio_info = pyqtSignal(list)

    def __init__(self, text_file: str) -> None:
        super(ReadTextFileThread, self).__init__()
        self.text_file = text_file

    def run(self) -> None:
        contents = open(self.text_file, encoding="utf-8").readlines()
        audio2text = []
        logging.info(f"Number of text information is {len(contents) - 1}")
        for line in contents[1:]:
            audio_name, rec_result, ref_result = line.strip().split("\t")
            audio_list = [audio_name, rec_result, ref_result]
            audio2text.append(audio_list)

        self.audio_info.emit(audio2text)


class FindAudioThread(QThread):
    audio_info = pyqtSignal(dict)

    def __init__(self, audio_dir: str) -> None:
        super(FindAudioThread, self).__init__()
        self.audio_dir = audio_dir

    def run(self):
        audio2path = {}
        audio_files = Path(self.audio_dir).rglob("*.wav")
        for audio_file in audio_files:
            audio_file = str(audio_file)
            audio_name = os.path.basename(audio_file)
            audio2path[audio_name] = audio_file

        logging.info(f"Found {len(audio2path.keys())} wav files.")

        self.audio_info.emit(audio2path)


class PlayAndStopThread(QThread):
    CHUNK = 1024

    def __init__(self, wav_path: str) -> None:
        super(PlayAndStopThread, self).__init__()
        self.wavp = wav_path
        self.stop = False

    def accept(self) -> None:
        self.stop = True

    def run(self) -> None:
        logging.info(f"Start to play wav file: {self.wavp}.")
        wf = wave.open(self.wavp, 'rb')
        p = pyaudio.PyAudio()  # 创建一个播放器
        # 打开数据流
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        # 读取数据
        data = wf.readframes(self.CHUNK)

        # 播放
        while data != '':
            if self.stop:
                return
            stream.write(data)
            data = wf.readframes(self.CHUNK)

        # 停止数据流
        stream.stop_stream()
        stream.close()

        # 关闭 PyAudio
        p.terminate()
        logging.info(f"End to play wav file: {self.wavp}.")
