# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 23:10:34 2022

@author: muxia
"""


from PyQt5.QtWidgets import QApplication,QWidget,QTextEdit,QVBoxLayout,QPushButton
import sys

class TextEditDemo(QWidget):
    def __init__(self,parent=None):
        super(TextEditDemo, self).__init__(parent)
        self.setWindowTitle('QTextEdit 例子')

        #定义窗口的初始大小
        self.resize(300,270)
        #创建多行文本框
        self.textEdit=QTextEdit()
        #创建两个按钮
        self.btnPress1=QPushButton('显示文本')
        self.btnPress2=QPushButton('显示HTML')

        #实例化垂直布局
        layout=QVBoxLayout()
        #相关控件添加到垂直布局中
        layout.addWidget(self.textEdit)
        layout.addWidget(self.btnPress1)
        layout.addWidget(self.btnPress2)

        #设置布局
        self.setLayout(layout)

        #将按钮的点击信号与相关的槽函数进行绑定，点击即触发
        self.btnPress1.clicked.connect(self.btnPress1_clicked)
        self.btnPress2.clicked.connect(self.btnPress2_clicked)

    def btnPress1_clicked(self):
        #以文本的形式输出到多行文本框
        self.textEdit.setPlainText('Hello PyQt5!\n单击按钮')

    def btnPress2_clicked(self):
        #以Html的格式输出多行文本框，字体红色，字号6号
        self.textEdit.setHtml("<font color='red' size='6'><red>Hello PyQt5!\n单击按钮。</font>")
        
if __name__ == '__main__':
    app=QApplication(sys.argv)
    win=TextEditDemo()
    win.show()
    sys.exit(app.exec_())