#!/usr/bin/env python
# coding=utf-8
from PyQt4.QtCore import *
import requests
import re
from OCR import Image2txt


def expRobot(search):
    path = '../OCR/tempimg/'
    url='https://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word='+search+'表情包'+'&ct=201326592&ic=0&lm=-1&width=&height=&v=flip'
    #url='http://image.baidu.com/search/flip?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1496141615672_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&ctd=1496141615672%5E00_1524X790&word=%E8%A1%A8%E6%83%85%E5%8C%85'
    html=requests.get(url).text
    pic_url=re.findall('"objURL":"(.*?)",',html,re.S)
    i = 0
    for each in pic_url:
        print(each)
        try:
            pic=requests.get(each,timeout=10)
        except requests.exceptions.ConnectionError:
            print('error')
            continue
        imgpath=path + str(i) + '.jpg'
        fp = open(imgpath,'wb')
        fp.write(pic.content)
        fp.close()
        i += 1
        try:
            pic = Image2txt.picture_ocr(imgpath)
            txt = pic.get_crop_txt()
            print(txt)
      #  if txt is ok
        except AttributeError as e:
            continue
        if not txt:
            print('ocr failed %s', '放弃')
            continue
        else:
            return imgpath


class backEnd(QThread):

    finish_signal = pyqtSignal(str, bool)
    def __init__(self, txt):
        super(backEnd, self).__init__()
        self.txt = txt

    def run(self):
        path = expRobot(self.txt)
        self.finish_signal.emit(path, True)

