# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 18:35:08 2022

@author: DuHu

创建一些与界面无关的函数
- 创建和读取数据库；
- 数据库数据按照固定格式导出；
- 读取comments选项文件
"""
import os
import sys


def read_comments_file(text_file_path: str) -> list:
    comments = []
    with open(text_file_path, 'r', encoding='utf-8-sig') as f:
        contents = f.readlines()
        for line in contents:
            comments.append(line.strip())
    return comments
