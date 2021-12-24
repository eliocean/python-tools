# encoding=utf-8

import os
from io import StringIO
from io import open
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, process_pdf


# 获取文件列表
def getPDFfiles(path):
    PDFFileList = []
    for home, dirs, files in os.walk(path):
        for filename in files:
            # PDFFileList.append(filename) #文件名列表，只包含文件名
            if filename.endswith("pdf"):
                PDFFileList.append(os.path.join(home, filename))  # 包含完整路径

    return PDFFileList


def read_pdf(path):
    # resource manager
    with open(path, "rb") as pdf:
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        # device
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        process_pdf(rsrcmgr, device, pdf)
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
        for line in lines:
            if words in line:
                print("["+pdffile+"]->"+line)
