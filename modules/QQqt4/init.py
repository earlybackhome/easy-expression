# -*- coding: utf-8 -*-
from PyQt4.Qt import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pyqtChatApp import PyqtChatApp
import re
import sys, os
sys.path.append('..')
from OCR import Image2txt

QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))


class Backend(QThread):
	update_date = pyqtSignal(str, int)
	close_signal = pyqtSignal()
	def __init__(self, progess):
		super(Backend, self).__init__()
		self.progess = progess

	def run(self):
		Image_dir = '../OCR/img/'
		print(__file__)
		out = open('../OCR/biaoqing.txt', 'a')
		checked_info = open('../OCR/checked.info', 'a+')
		checked_info.seek(0)
		checked_filelist = checked_info.readlines()
		os.chdir(Image_dir)
		filenum = 0
		count = 0
		self.files = os.listdir()
		self.num = int(os.popen('ls -R | wc -w').read()) - int(os.popen('ls | wc -w').read())
		self.progess.progressBar.setMaximum(self.num)
		for subdir in self.files:
			if  not os.path.isdir(subdir):
				continue
			for filename in os.listdir(subdir):
				count += 1
				info = []
				fulladdress = '/'.join((Image_dir ,subdir ,filename))
				# print('filename: %s', fulladdress)
				#两种不会继续分析的情况，一种是在checked_info中存在，一种是后缀为.jpg
				if fulladdress + '\n' in checked_filelist :
					# print('%s 已存在', fulladdress)
					continue
				else :
					checked_info.write(fulladdress + '\n')
				if os.path.splitext(filename)[1] != '.jpg':
					continue
				info.extend([subdir, filename])
				#试图对图片做OCR如果ＯＣＲ结果是空字符或者发生错误都放弃OCR
				try:
					pic_ocr = Image2txt.picture_ocr(subdir +'/' + filename)
					txt = pic_ocr.get_crop_txt()
					# print('pre: %s', txt)
					txt = re.subn(r'[^\w\u4e00-\u9fa5]+','', txt)[0].strip()
					# print("after: %s", txt)
					info.append(txt)
				except AttributeError as e:
					continue
				if not txt:
					print('ocr failed %s', '放弃')
					info.append('放弃')
					continue
				write_string = txt + '#' + Image_dir + '/' + subdir + '/' + filename +'\n'
				# print(write_string)
				info = 'checking:  ' + '\\'.join(info)
				print(info)
				self.update_date.emit(info, count)
				# self.detail.append(info)
				out.write(write_string)
			filenum += 1
			if filenum > 2:
				break
		self.update_date.emit('此文件夹下所有的图片已经OCR', self.num)
		out.close()
		checked_info.close()
		os.chdir('../../QQqt4')
		self.close_signal.emit()

		self.progess.close()

class Progess(QDialog):

	def __init__(self, parent=None):
		super(Progess,self).__init__(parent)
		typeLabel=QLabel(self.tr("installing..."))
		self.btnSize = 35
		self.setFixedSize(700, 500)

		selectdir = QPushButton()
		selectdir.setStyleSheet("QPushButton{border-image:url(icons/dictionary.png);}"#这个参数可以让图片随大小缩放
			 "QPushButton:hover{border: 2px groove blue;}"
			 "QPushButton:pressed{border-style: inset;}")
		selectdir.setFixedSize(self.btnSize,self.btnSize)
		selectdir.clicked.connect(self.selectDir)

		self.line=QLineEdit('../OCR/img/')
		self.detail = QTextEdit('详细信息...')
		self.detail.setFont(QFont("Microsoft Yahei",13,QFont.Normal))
		self.detail.NoWrap = True

		startPushButton=QPushButton(self.tr("开始"))
		startPushButton.setFont(QFont("Microsoft YaHei",15,QFont.Bold))

		self.layout=QGridLayout()
		self.layout.addWidget(typeLabel,1,0)
		self.layout.addWidget(startPushButton,1,6)
		self.layout.addWidget(QLabel(self.tr("请选择表情所在文件夹")), 0, 0, 1, 3)
		self.layout.addWidget(selectdir,1, 5)
		self.layout.addWidget(self.line, 1, 0, 1, 5)
		# self.layout.addWidget(QLabel(self.tr("处理进度")), 3, 0)
		self.progressBar=QProgressBar()
		self.layout.addWidget(self.progressBar,2,0,1,7)
		self.progressBar.setMinimum(0)

		cursor = self.detail.textCursor()
		cursor.movePosition(QTextCursor.End)
		self.detail.setTextCursor(cursor)

		self.layout.setMargin(15)
		self.layout.setSpacing(10)
		self.layout.addWidget(self.detail, 3, 0, 1, 7)

		self.setLayout(self.layout)

		self.connect(startPushButton,SIGNAL("clicked()"),self.slotStart)
		self.b = Backend(self)

	def slotStart(self):
		global path
		path = str(self.line.text())
		self.b.update_date.connect(self.update)
		self.b.start()
		# self.close()

	def update(self, txt, count):
		self.detail.append(txt)
		self.progressBar.setValue(count)

	def selectDir(self):
		# print ("OnClickmenuSetFileSaveDir")
		tmpDir = QFileDialog.getExistingDirectory()
		if(len(tmpDir) > 0):
			self.SaveDir = tmpDir
			self.line.setText(tmpDir)
			if not os.path.exists(self.SaveDir):
				os.mkdir(self.SaveDir)


if __name__ == '__main__':
	path = os.getcwd()
	app=QApplication(sys.argv)
	progess=Progess()
	progess.show()
	app.exec_()

	pchat = PyqtChatApp(path)
	pchat.show()
	sys.exit(app.exec_())
