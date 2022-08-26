# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 16:49:48 2022

@author: duhu
"""


#-*-coding:utf-8-*-

#引入库
import pyaudio
import wave
import sys

# 定义数据流块
CHUNK = 1024

# if len(sys.argv) < 2:
#     print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
#     sys.exit(-1)
class playWavAudio():
    def __init__(self):
        #只读方式打开wav文件
        self.wf = wave.open(r'data/1b_10036.wav', 'rb')   #(sys.argv[1], 'rb')
    def play(self):

        p = pyaudio.PyAudio()   #创建一个播放器

        # 打开数据流
        stream = p.open(format=p.get_format_from_width(self.wf.getsampwidth()),
                        channels=self.wf.getnchannels(),
                        rate=self.wf.getframerate(),
                        output=True)

        # 读取数据
        data = self.wf.readframes(CHUNK)

        # 播放
        while data != '':
            stream.write(data)
            data = self.wf.readframes(CHUNK)

        # 停止数据流
        stream.stop_stream()
        stream.close()

        # 关闭 PyAudio
        p.terminate()

if __name__ == "__main__":
    aaa = playWavAudio()
    aaa.play()
