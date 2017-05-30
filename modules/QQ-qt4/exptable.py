import sys, os
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class Window(QWidget):

	def __init__(self, listView, path=os.getcwd()):

		super(Window, self).__init__()
		self.listView = listView
		self.resize(680, 450)
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setStyleSheet("QScrollBar{width:0;height:0}")
		lo = QGridLayout()
		self.table = MyTable(self.listView, self, path)
		self.table.move(10,15)
		lo.addWidget(self.table)
		self.setLayout(lo)
		self.move(QCursor.pos().x()-100, QCursor.pos().y()-470)
		self.setStyleSheet("QTableWidget{background: #74C5FA;border:2px groove gray;border-radius:10px;padding:2px 4px;}"
		    "QLabel{background: white;color: blue;border-width: 2px; border-style: solid;border-color: #74C5FA;border-radius:2px}")

	def paintEvent(self, event):
		if self.listView.expcalling == True:

			self.qp = QPainter(self)

			self.qp.begin(self)
			self.qp.setPen(Qt.black)
			self.qp.setBrush(QColor("#74C5FA"))
			size = self.size()
			w = 680
			h = 450
			self.trigon = 20
			self.xborder =10
			self.yborder =20
			middle = 100
			shiftx = self.trigon/2
			shifty = self.trigon*3**0.5/2
			self.pL = QPolygonF()
			self.pL.append(QPointF(self.xborder,self.yborder)) #起始点
			self.pL.append(QPointF(self.xborder, h-self.yborder)) # 第二点
			self.pL.append(QPointF(middle-shiftx, h-self.yborder)) #第三点
			self.pL.append(QPointF(middle, h-self.yborder+shifty)) #第四点
			self.pL.append(QPointF(middle+shiftx, h-self.yborder)) #第五点
			self.pL.append(QPointF(w-self.xborder, h-self.yborder)) #第六点
			self.pL.append(QPointF(w-self.xborder, self.yborder)) #第七点
			self.qp.drawPolygon(self.pL)
			self.qp.end()


class MyLabel(QLabel):
	def __init__(self, img, mytable, window, listView):
		super(MyLabel, self).__init__()
		self.listView = listView
		self.mytable = mytable
		self.window = window
		self.img = img
		self.expwid = 80
		pixmap = QPixmap(img)
		pixmap = pixmap.scaledToWidth(self.expwid)
		self.setPixmap(pixmap)


	def contextMenuEvent(self,event):
		delExp = QAction(QIcon('icons/delete.png'),u'删除',self)
		delExp.triggered.connect(self.delExpItem)#选中就会触发

		menu = QMenu()
		menu.addAction(delExp)
		menu.exec_(QCursor.pos())#全局位置比较好，使用e.pos()还得转换

		event.accept() #禁止弹出菜单事件传递到父控件中

	def delExpItem(self,b):
		os.remove(self.img)
		self.window.close()
		self.listView.expcalling = False


class MyTable(QTableWidget):

	def __init__(self, listView, window, path = os.getcwd()):
		super(MyTable, self).__init__()
		self.columncount = 8
		self.labels = []
		self.path = path
		self.window = window
		self.listView = listView
		self.setFixedSize(650, 400)
		self.setFrameShape(QFrame.NoFrame)
		self.setShowGrid(False)
		self.fillTable(path)
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.setStyleSheet("QScrollBar{width:10;height:0}")

	def fillTable(self, path):
		self.piclist = sorted(os.listdir(path))
		self.rowcount = len(self.piclist) // self.columncount + 1
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.setSelectionMode(QAbstractItemView.SingleSelection)
		self.verticalHeader().setVisible(False)
		self.horizontalHeader().setVisible(False)
		self.setRowCount(self.rowcount)
		self.setColumnCount(self.columncount)
		# self.setShowGrid(False) # hide the edge

		count = 0
		for picture in self.piclist:
			img = os.path.join(path, picture)
			self.labels.append(MyLabel(img, self, self.window, self.listView))
			self.setCellWidget(count//self.columncount, count%self.columncount, self.labels[count])
			count += 1
		self.resizeColumnsToContents()   #将列调整到跟内容大小相匹配
		self.resizeRowsToContents()      #将行大小调整到跟内容的大学相匹配
		self.move(0, 0)

		self.cellClicked.connect(self.on_click_del_table)
		self.show()

	def on_click_del_table(self, row, col):
		self.listView.expcalling = False
		self.listView.addImageMsg(self.path+self.piclist[col+row*self.columncount], False)
		self.listView.mywindow.close()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = MyTable('/home/qjy/Desktop/img/19/')
	# ex.paintEvent()
	ex.show()
	sys.exit(app.exec_())
