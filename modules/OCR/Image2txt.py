#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-05-29 23:29:00
# @Author  : SizheRee(sizheree.github.io)
# @Link    : http://sizheree.github.io
# @Version : $1.0

import cv2
import pyocr
import numpy as np
import sklearn.cluster as cl
import os
import PIL.Image as PI
import matplotlib.pyplot as plt
import sklearn
import re
from functools import reduce
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
# create a handler
handler = logging.FileHandler('Image2txt' + '.log')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

class Contour():
	def __init__(self, Contour):
		self.Contour = Contour #
		self.Hull = None #
		self.BoundRect = [x,y,w,h] = cv2.boundingRect(Contour) #
		self.centorid = None #
		self.ContArea = None #
		self.analysis()
	def analysis(self):
		self.Hull = cv2.convexHull(self.Contour)
		M = cv2.moments(self.Hull)
		try:
			cx = int(M['m10']/M['m00'])
			cy = int(M['m01']/M['m00'])
			self.centorid = (cx, cy)
		except ZeroDivisionError as e:
			pass
		self.ContArea = cv2.contourArea(self.Hull)

class picture_ocr(object):
	def __init__(self, filename):
		self.filename = filename
		self.image_croped_list = []
		self.centroids = []
		self.Contour_list = []
		self.image_shape = None
		self._analysis()
		self.config()

	def config(self):
		self.tool  = pyocr.get_available_tools()[0]
		self.lang = 'chi_sim'

	def _analysis(self):
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3, 3))
		Contour_list = []
		try:
			img = cv2.imread(self.filename, 0)
			shape = np.array(img.shape, np.int0)
		except AttributeError as e:
			return None
		# 将图片较小的图片放大
		raw_w, raw_h = shape[0], shape[1]
		if raw_w < 400:
			img = cv2.resize(img, tuple(np.int0(shape/raw_w*400)))
		if raw_h < 400:
			img = cv2.resize(img, tuple(np.int0(shape/raw_h*400)))
		new_w, new_h = img.shape
		#ｃａｎｎｙ边缘算子
		img_canny = cv2.Canny(img, 150, 200)
		# 转化为ｂｇｒ
		#     img_display = cv2.cvtColor(img_canny, cv2.COLOR_GRAY2BGR)
		imgo, contours, hierarchy = cv2.findContours(img_canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

		for contour in contours:
			[x,y,w,h] = cv2.boundingRect(contour)
			if w < new_w*0.01 or h < new_h*0.01: #细小碎片丢弃
				continue
			Contour_list.append(Contour(contour)) #Contour_list
		try:
			#将所有的轮廓按照面积大小进行排序
			Contour_list = sorted(Contour_list, key=lambda x:x.ContArea, reverse=True)
			# 按照从大到小画边缘，如果满足条件的画就判断为字的边框画一条黑色边缘线隔绝
			for contour in Contour_list:
				img_display = cv2.drawContours(img_canny, [contour.Hull], 0, 255, -1)
				if contour.BoundRect[2] < new_w*0.01 or contour.BoundRect[2] > new_w*0.5:
					continue
				if contour.BoundRect[3] < new_h*0.01 or contour.BoundRect[3] > new_h*0.5:
					continue
				img_display = cv2.drawContours(img_display, [contour.Hull], 0, 0, 1)
			#　删除大块红色
			for contour in Contour_list:
				if  contour.BoundRect[2] > new_w*0.3 or contour.BoundRect[3] > new_h*0.3:
					img_display = cv2.drawContours(img_display, [contour.Hull], 0, 0, -1)
			# 删除最大块后女各色
			#　ｃｌｏｓｅ将边缘的缝隙合上
			img_display = cv2.morphologyEx(img_display, cv2.MORPH_CLOSE, (9, 9))

			#　　第二波处理
			Contour_list2 = []
			centroids = [] # centroids
			#黑色背景图
			img_bg = np.zeros(shape, np.int8)
			ret, img_thresh = cv2.threshold(img, 180 , 255, cv2.THRESH_BINARY_INV)
			kernel2 = cv2.getStructuringElement(cv2.MORPH_CROSS,(3 , 3))
			img_opened = cv2.morphologyEx(img_thresh,cv2.MORPH_OPEN, kernel2)
			imgo, contours, hierarchy = cv2.findContours(img_opened,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
			for contour in contours:
				[x2,y2,w2,h2] = cv2.boundingRect(contour)
				if w2 < new_w*0.03 or w2 > new_w*0.5 or\
				h2 < new_h*0.03 or h2 > new_h*0.5:
					continue
				centroids.append((x2+w2/2, y2+h2/2))#centroid?
				cv2.rectangle(img_bg, (x2, y2), (x2+w2,y2+h2),(255,255,255), -1)
				Contour_list2.append(Contour(contour))
		#   dbscan算法
			matrix = np.array(centroids)
			if(len(matrix) == 0):
				return None
			eps = (x + new_h)*0.2
		#         print('matrix len: %s'%len(matrix), centroids)
			ret, sk_index = sklearn.cluster.dbscan(matrix, eps, min_samples=1)
			true_centorids = [tuple(x) for x in matrix[sk_index==0]]
			test_list =  Contour_list2
			xmin, xmax, ymin, ymax = self.find_extrm(test_list)
			mask = np.zeros(img.shape, np.int8)
			mask[ymin:ymax, xmin:xmax] = 1
			img_display = cv2.bitwise_and(img_display, img_display, mask=mask)
			img_white = img_display

			img_blackbg = np.zeros(img_white.shape, np.int8)
			#display
			linesum = np.sum(img_white>1, axis=1)
			seg_list = self.segment(linesum)
			#滤去宽度小的行
			filte_list = list(filter(lambda x: x[1]-x[0]>(xmax-xmin)*0.08, seg_list))
			if(len(filte_list)!=0):
				for seg in seg_list:
					img_blackbg[seg[0], :] =255
				for filt in filte_list:
					for i in range(filt[0], filt[1]):
						img_blackbg[i][:linesum[i]] = 1
				k = 0
				for filt in filte_list:
					img_crop = img[filt[0]-1:filt[1], xmin:xmax]
					hi, wi= img_crop.shape
					hi += 6
					wi += 6
					img_crop_bg = np.ones((hi, wi))*255
					img_crop_bg[3:-3, 3:-3] = img_crop
					self.image_croped_list.append(img_crop_bg)
			else:
				return None
		except ValueError as e:
			pass
		return None

	def find_extrm(self, test_list):
		ymin = xmin = 1000
		ymax = xmax = 0
		for cont in test_list:
			x, y, w, h = cont.BoundRect
			xmin = x if x < xmin else xmin
			xmax = x+w if x+w > xmax else xmax
			ymin = y if y < ymin else ymin
			ymax = y+h if y+h > ymax else ymax
		return (xmin, xmax, ymin, ymax)
	def segment(self, linesum, mode=0):
		seg_list = []
		a= list((np.int8(linesum>5)))
		if mode==1:
			print(a)
		a[0] = str(a[0])
		s = reduce(lambda x, y: x+str(y), a)
		itera = re.finditer(r'1+', s)
		for i in itera:
			seg_list.append(i.span())
		return seg_list
	def get_txt(self):
		if not self.image_croped_list:
			self._analysis()
		txt_list = []
		for i in self.image_croped_list:
			txt = self.tool.image_to_string(PI.fromarray(i), lang=self.lang,
											builder=pyocr.builders.TextBuilder())
			txt_list.append(txt)
		return txt_list
	def get_crop_txt(self):
		img_croped_list = self.image_croped_list
		txt_list = []
		if not self.image_croped_list:
			self._analysis()
		for img_croped in img_croped_list:
			if img_croped.shape[0] <60:
				xs, ys = img_croped.shape
				log.debug('xs, ys%s', (xs, ys))
				xs, ys = 60, int(60/xs*ys)+2

				img_croped = cv2.resize(img_croped, (ys ,xs))
			if img_croped.shape[1] < 200:
				xs, ys = img_croped.shape
				xs, ys = int(200/ys*xs), 200
				img_croped = cv2.resize(img_croped, (ys ,xs))

			txt = self.tool.image_to_string(PI.fromarray(img_croped), lang=self.lang,
											builder=pyocr.builders.TextBuilder())
			log.debug('in txt %s', txt)
			txt_list.append(txt)
		return ''.join(txt_list)


if __name__  == '__main__':
	log.setLevel(logging.INFO)
	#设置两个路径参数
	Image_dir = os.path.split(__file__)[0] + '/img/'
	print(Image_dir)
	out = open('./biaoqing.txt', 'a')

	log.debug('oh ? %s', 'checked.info' not  in os.listdir())

	checked_info = open('checked.info', 'a+')
	checked_info.seek(0)
	checked_filelist = checked_info.readlines()

	os.chdir(Image_dir)
	count = 0
	for subdir in os.listdir():
		if  not os.path.isdir(subdir):
			continue
		for filename in os.listdir(subdir):
			fulladdress = '/'.join((Image_dir ,subdir ,filename))
			log.debug('filename: %s', fulladdress)
			#两种不会继续分析的情况，一种是在checked_info中存在，一种是后缀为.jpg
			if fulladdress + '\n' in checked_filelist :
				log.info('%s 已存在', fulladdress)
				continue
			else :
				checked_info.write(fulladdress + '\n')
			if os.path.splitext(filename)[1] != '.jpg':
				continue
			#试图对图片做OCR如果ＯＣＲ结果是空字符或者发生错误都放弃OCR
			try:
				pic_ocr = picture_ocr(subdir +'/' + filename)
				txt = pic_ocr.get_crop_txt()
				log.debug('txt:%s', txt)
				log.debug('pre: %s', txt)
				txt = re.subn(r'[^\w\u4e00-\u9fa5]+','', txt)[0].strip()
				log.info("after: %s", txt)
			except AttributeError as e:
				log.debug('error%s', e)
				raise e
			if not txt:
				log.info('ocr failed %s', '放弃')
				continue
			write_string = txt + '#' + Image_dir + subdir + '/' + filename +'\n'
			log.debug(write_string)
			out.write(write_string)
		count += 1
		if count > 3:
			break
	out.close()
	checked_info.close()
