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
    print(read_pdf("test.pdf"))

