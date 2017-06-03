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
		self.Contour = Contour
		self.BoundRect = [x,y,w,h] = cv2.boundingRect(Contour)
		self.centorid = (x+w/2, y+h/2)

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
		img_gray  = cv2.imread(self.filename, 0)
		if img_gray.shape[0] < 300:
			xg, yg = img_gray.shape
			xg, yg = 300, int(300/xg*yg)
			img_gray = cv2.resize(img_gray, (xg, yg))

		self.image_shape = img_gray.shape
		img_bg = np.zeros(self.image_shape, dtype=img_gray.dtype)
		ret, img_thresh = cv2.threshold(img_gray, 180 , 255, cv2.THRESH_BINARY_INV)
		kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3 , 3))
		img_opened = cv2.morphologyEx(img_thresh,cv2.MORPH_OPEN, kernel)

		img2, contours, hierarchy = cv2.findContours(img_opened,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
		for contour in contours:
			[x,y,w,h] = cv2.boundingRect(contour)
			if w < self.image_shape[0]*0.03 or w > self.image_shape[0]*0.5 or\
			h < self.image_shape[1]*0.03 and h > self.image_shape[1]*0.5:
				continue
			self.centroids.append((x+w/2, y+h/2))#centroid?
			cv2.rectangle(img_bg, (x, y), (x+w,y+h),(255,255,255), -1)
			self.Contour_list.append(Contour(contour))

#         dbscan
		matrix = np.array(self.centroids)
		try:
			eps = (self.image_shape[0] + self.image_shape[1])*0.2
			ret, index = sklearn.cluster.dbscan(matrix, eps, min_samples=1)
			true_centorids = [tuple(x) for x in matrix[index==0]]
			test_list = list(filter(lambda x:x.centorid in true_centorids, self.Contour_list))
			xmin, xmax, ymin, ymax = self.find_extrm(test_list)
			self.image_croped = img_gray[ymin:ymax+1, xmin:xmax]
		except ValueError as e:
			log.debug('valueError%s', e)
			raise AttributeError

		# process img_bg
		img_bg = cv2.dilate(img_bg, kernel, iterations=3)
		img_bg, text_contours, hierarchy = cv2.findContours(img_bg, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
		for contour in text_contours:
			[x,y,w,h] = cv2.boundingRect(contour)
			self.image_croped_list.append(img_gray[y:y+h, x:x+w])
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
		img_croped = self.image_croped
		if not self.image_croped_list:
			self.analysis()
		if img_croped.shape[0] <60:
			xs, ys = img_croped.shape
			log.debug('xs, ys%s', (xs, ys))
			xs, ys = 60, int(60/xs*ys)+2

			img_croped = cv2.resize(img_croped, (ys ,xs))
		if img_croped.shape[1] < 200:
			xs, ys = img_croped.shape
			xs, ys = int(200/ys*xs), 200
			img_croped = cv2.resize(img_croped, (ys ,xs))

		img_croped = cv2.bitwise_not(img_croped)
		txt = self.tool.image_to_string(PI.fromarray(img_croped), lang=self.lang,
										builder=pyocr.builders.TextBuilder())
		return txt


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
				log.debug('pre: %s', txt)
				txt = re.subn(r'[^\w\u4e00-\u9fa5]+','', txt)[0].strip()
				log.info("after: %s", txt)
			except AttributeError as e:
				continue
			if not txt:
				log.info('ocr failed %s', '放弃')
				continue
			write_string = txt + '#' + Image_dir + subdir + '/' + filename +'\n'
			log.debug(write_string)
			out.write(write_string)
		count += 1
		if count > 100:
			break
	out.close()
	checked_info.close()
