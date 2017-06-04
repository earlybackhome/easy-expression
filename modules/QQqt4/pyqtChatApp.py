#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-12-08 10:56:55
# @Author  : He Liang (helianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT

import os,sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from mycopygroupuserlist import GroupUserList
from mycopymsglist import MsgList
from flowlayout import FlowLayout
from exprobot import backEnd
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

DEFAULT_HEAD = 'icons/qq.png'


class TextEdit(QTextEdit,QObject):
    '''支持enter/return信号发射的QTextEdit'''
    entered = pyqtSignal()
    ctrlentered = pyqtSignal()
    def __init__(self, msglist = None, parent = None):
        super(TextEdit, self).__init__(parent)
        self.msglist = msglist

    def keyPressEvent(self,e):
        # print e.key() == Qt.Key_Return,e.key() == Qt.Key_Enter, e.modifiers() == Qt.ControlModifier
        if (e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter) and (e.modifiers() != Qt.ControlModifier):# and (e.modifiers() == Qt.ControlModifier):
            self.entered.emit()# return 输入
        if (e.key() == Qt.Key_Return) and (e.modifiers() == Qt.ControlModifier):
            self.ctrlentered.emit()
        super(TextEdit,self).keyPressEvent(e)
        if (e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter):
            self.clear()

    def mousePressEvent(self, event):
        if self.msglist.expcalling == True:
            self.msglist.mywindow.close()
            self.msglist.expcalling = False
        if self.msglist.bestexpcalling == True:
            self.msglist.bestwindow.close()
            self.msglist.bestexpcalling = False

    def onTextChanged(self, event):
        print(self.toPlainText())

'''
"QPushButton{background-color:black;color: white;border-radius: 10px;border: 2px groove gray;border-style: outset;}"
"QPushButton:hover{background-color:white; color: black;}"
"QPushButton:pressed{background-color:rgb(85, 170, 255);border-style: inset;}"
'''
class MsgInput(QWidget,QObject):
    '''自定义的内容输入控件，支持图像和文字的输入，文字输入按回车确认。'''
    textEntered = pyqtSignal(str)
    imgEntered = pyqtSignal(str)
    ctrlEntered = pyqtSignal(str)

    btnSize = 35
    teditHeight = 200
    def __init__(self, msglist, parent = None):
        self.msglist = msglist
        super(MsgInput, self).__init__(parent)
        self.setContentsMargins(3,3,3,3)

        self.textEdit = TextEdit(msglist)
        self.textEdit.setMaximumHeight(self.teditHeight)
        self.setMaximumHeight(self.teditHeight+self.btnSize)
        self.textEdit.setFont(QFont("Microsoft Yahei",20,QFont.Normal))
        self.textEdit.entered.connect(self.sendText)
        self.textEdit.ctrlentered.connect(self.selectImg)

        sendImg = QPushButton()
        sendImg.setStyleSheet("QPushButton{border-image:url(icons/img.png);}"#这个参数可以让图片随大小缩放
             "QPushButton:hover{border: 2px groove blue;}"
             "QPushButton:pressed{border-style: inset;}")
        sendImg.setFixedSize(self.btnSize,self.btnSize)
        sendImg.clicked.connect(self.sendImage)

        sendTxt = QPushButton(u'发送')
        sendTxt.setFont(QFont("Microsoft YaHei",15,QFont.Bold))
        sendTxt.setFixedHeight(self.btnSize)
        sendTxt.clicked.connect(self.sendText)

        sendExp = QPushButton()
        sendExp.setStyleSheet("QPushButton{border-image:url(icons/expr.png);}"
            "QPushButton:hover{border:2px groove blue;}"
            "QPushButton:pressed{border-style: inset;}")
        sendExp.setFixedSize(self.btnSize, self.btnSize)
        # sendExp.clicked.connect(self.sendExpression)
        sendExp.clicked.connect(self.msglist.addExpList)

        hl = FlowLayout()
        hl.addWidget(sendExp)
        hl.addWidget(sendImg)
        hl.addWidget(sendTxt)
        hl.setMargin(0)

        vl = QVBoxLayout()
        vl.addLayout(hl)
        vl.addWidget(self.textEdit)
        vl.setMargin(0)
        self.setLayout(vl)

    def sendImage(self):#选择图像发送

        if msglist.expcalling == True:
            msglist.mywindow.close()
            msglist.expcalling == False
        if msglist.bestexpcalling == True:
            msglist.bestwindow.close()
            msglist.expcalling == False
        dialog = QFileDialog(self,u'请选择图像文件...')
        dialog.setDirectory(os.getcwd() + '/ref') #设置默认路径
        dialog.setNameFilter(u"图片文件(*.png *.gif *.jpg *.bmp *.ico);;")#中间一定要用两个分号才行！
        if dialog.exec_():
            selectFileName = dialog.selectedFiles()[0]
            self.imgEntered.emit(selectFileName)
        else:#放弃选择
            pass

    def sendText(self):
        if self.msglist.expcalling == True:
            self.msglist.mywindow.close()
            self.msglist.expcalling == False
        if self.msglist.bestexpcalling == True:
            self.msglist.bestwindow.close()
            self.msglist.expcalling == False
        txt = self.textEdit.toPlainText()
        if len(txt)>0:
            self.textEntered.emit(txt)
            self.textEdit.clear()

    def selectImg(self):
        if self.msglist.expcalling == True:
            self.msglist.mywindow.close()
            self.msglist.expcalling == False
        if self.msglist.bestexpcalling == True:
            self.msglist.bestwindow.close()
            self.msglist.expcalling == False
        txt = self.textEdit.toPlainText()
        if len(txt)>0:
            self.msglist.selectImage(txt)


class Back(QThread):
    send_signal = pyqtSignal(str)
    def __init__(self, txt, robot):
        super(Back, self).__init__()
        self.txt = txt
        self.robot = robot

    def run(self):
        self.send_signal.emit(str(self.robot.get_response(self.txt)))


class PyqtChatApp(QSplitter):
    """聊天界面，QSplitter用于让界面可以鼠标拖动调节"""
    curUser = {'id':None,'name':None,'head':DEFAULT_HEAD}
    selfHead = DEFAULT_HEAD
    def __init__(self, path = os.getcwd()):
        super(PyqtChatApp, self).__init__(Qt.Horizontal)

        self.setWindowTitle('pyChat') # window标题
        self.setWindowIcon(QIcon('icons/chat.png')) #ICON
        self.setMinimumSize(1000,800) # 窗口最小大小

        self.ursList = GroupUserList()
        self.ursList.setMaximumWidth(250)
        self.ursList.setMinimumWidth(180)
        self.ursList.itemDoubleClicked.connect(self.setChatUser)
        self.msgList = MsgList(path)
        self.msgList.setStyleSheet("background-color: #F6F4F9")
        self.msgList.setDisabled(True) #刚打开时没有聊天显示内容才对
        self.ursList.msglist = self.msgList
        self.msgInput = MsgInput(self.msgList)
        self.msgInput.textEntered.connect(self.sendTextMsg)
        self.msgInput.imgEntered.connect(self.sendImgMsg)
        # self.msgInput.textEdit.textChanged.connect(self.msgList.selectImage)

        self.ursList.setParent(self)
        rSpliter = QSplitter(Qt.Vertical, self)
        self.msgList.setParent(rSpliter)
        self.msgInput.setParent(rSpliter)

        self.chatbot = ChatBot("myBot", read_only = True, storage_adapter="chatterbot.storage.JsonFileStorageAdapter")
        self.chatbot.set_trainer(ChatterBotCorpusTrainer)
        self.chatbot.train("chatterbot.corpus.chinese")

        self.setDemoUser() #模拟添加用户

    def setDemoMsg(self):
        self.msgList.clear()
        self.msgList.addTextMsg("Hello",True,self.curUser['head'])
        self.msgList.addTextMsg("World!",False,self.selfHead)
        self.msgList.addTextMsg(u"昨夜小楼又东风，春心泛秋意上心头，恰似故人远来载乡愁，今夜月稀掩朦胧，低声叹呢喃望星空，恰似回首终究一场梦，轻轻叹哀怨...",True,self.curUser['head'])
        self.msgList.addTextMsg(u"With a gentle look on her face, she paused and said,她脸上带着温柔的表情，稍稍停顿了一下，便开始讲话",False,self.selfHead)
        self.msgList.addImageMsg('ref/bq.gif',True,self.curUser['head'])
        # self.msgList.addImageMsg('ref/mt.gif',False,self.selfHead)

    def setDemoUser(self):
        self.ursList.clear()
        self.ursList.addUser('hello world')
        self.ursList.addUser('表情包助手')
        self.ursList.addGroup('group')
        self.ursList.addUser('思吉吉',group = 'group')
        self.ursList.addGroup(u'中文')
        self.ursList.addUser(u'田心吉吉',group = u'中文',head = 'icons/hd_1.png')


    def mousePressEvent(self, event):
        if self.msgList.expcalling == True:
            self.msgList.mywindow.close()
            self.msgList.expcalling = False
        if self.msgList.bestexpcalling == True:
            self.msgList.bestwindow.close()
            self.msgList.bestexpcalling == False


    @pyqtSlot(str)
    def sendTextMsg(self,txt):
        # txt = unicode(txt)
        self.msgList.addTextMsg(txt,False)
        if self.curUser['name'] == '表情包助手':
            self.imgget = backEnd(txt)
            self.imgget.start()
            self.imgget.finish_signal.connect(self.msgList.addImageMsg)
        else:
            self.robotstart = Back(txt, self.chatbot)
            self.robotstart.start()
            self.robotstart.send_signal.connect(self.robotSend)
            # self.msgList.addTextMsg(str(self.chatbot.get_response(txt)), True, self.curUser['head'])

    def robotSend(self, txt):
        self.msgList.addTextMsg(txt, True, self.curUser['head'])

    @pyqtSlot(str)
    def sendImgMsg(self,img):
        # img = unicode(img)
        self.msgList.addImageMsg(img,False)

    @pyqtSlot(QListWidgetItem)
    def setChatUser(self,item):
        (self.curUser['id'],self.curUser['name'],self.curUser['head']) = (item.getId(),item.getName(),item.getHead())
        self.msgList.setDisabled(False)
        self.setWindowTitle('pyChat: chating with %s...'% self.curUser['name'])
        self.setDemoMsg()

    def closeEvent(self, event):
        if self.msgList.expcalling == True:
            self.msgList.mywindow.close()

        if self.msgList.bestexpcalling == True:
            self.msgList.bestwindow.close()

        os.system('rm ../OCR/tempimg/*')


if __name__=='__main__':
    app = QApplication(sys.argv)
    pchat = PyqtChatApp('../OCR/img/')
    pchat.show()
    sys.exit(app.exec_())
