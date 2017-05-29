import sys, os
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class MyTable(QTableWidget):

	def __init__(self, path = os.getcwd()):
		super(MyTable, self).__init__()
		self.columncount = 11
		self.labels = []
		self.expwid = 60
		self.fillTable(path)


	def fillTable(self, path):
		self.piclist = os.listdir(path)
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
			pixmap = QPixmap(img)
			pixmap = pixmap.scaledToWidth(self.expwid)
			self.labels.append(QLabel())
			self.labels[count].setPixmap(pixmap)
			self.setCellWidget(count//self.columncount, count%self.columncount, self.labels[count])
			count += 1
		self.resizeColumnsToContents()   #将列调整到跟内容大小相匹配
		self.resizeRowsToContents()      #将行大小调整到跟内容的大学相匹配
		self.move(0, 0)

		# self.cellClicked.connect(self.on_click_del_table)


	def mousePressEvent(self, event):
		print(event.pos())


		# mouse = QMouseEvent()
		# mouse


	# def paintEvent(self):
	# 	qp = QPainter(self)

	# 	qp.setPen(Qt.black)
	# 	qp.setBrush(QColor("#aaaaaa"))
	# 	size = self.size()

	# 	w = 500
	# 	h = 300
	# 	self.trigon = 20
	# 	self.border =5
	# 	middle = h/2
	# 	shiftx = self.trigon/2
	# 	shifty = self.trigon*3**0.5/2
	# 	pL = QPolygonF()
	# 	pL.append(QPointF(self.border,self.border)) #起始点
	# 	pL.append(QPointF(self.border, h+self.border)) # 第二点
	# 	pL.append(QPointF(w/2-shiftx, h+self.border)) #第三点
	# 	pL.append(QPointF(w/2, h+self.border+shifty)) #第四点
	# 	pL.append(QPointF(w/2+shiftx, h+self.border)) #第五点
	# 	pL.append(QPointF(w, h+self.border)) #第六点
	# 	pL.append(QPointF(w, self.border)) #第七点
	# 	qp.drawPolygon(pL)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = MyTable('/home/qjy/Desktop/img/19/')
	# ex.paintEvent()
	ex.show()
	sys.exit(app.exec_())
