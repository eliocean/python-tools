#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:Eli
# datetime:2021/8/25 14:24
# software: PyCharm

import os
from io import StringIO
from io import open
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter


# 获取文件列表
from pdfminer.pdfpage import PDFPage


def getPDFfiles(path):
    PDFFileList = []
    for home, dirs, files in os.walk(path):
        for filename in files:
            # PDFFileList.append(filename) #文件名列表，只包含文件名
            if filename.endswith("pdf"):
                PDFFileList.append(os.path.join(home, filename))  # 包含完整路径

    return PDFFileList


def read_pdf(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    # device
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    with open(path, 'rb') as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp):
            page.rotate = (page.rotate) % 360
            interpreter.process_page(page)
    device.close()
    content = retstr.getvalue()
    retstr.close()
    # 获取所有行
    lines = str(content).split("\n")
    return lines




if __name__ == '__main__':
    words = input("请输入要检索的字符串：\n")
    pdffiles = getPDFfiles("./")
    for pdffile in pdffiles:
        lines = read_pdf(pdffile)
        # print("".join(lines))
        for line in lines:
            if words in line:
                print("["+pdffile+"]->"+line)

