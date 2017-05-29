#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2017-05-28 10:13:14
# @Author  : Sizheree (sizheree.github.io)
# @Link    :
# @Version : $1.0$

import logging
import time
import numpy as np
import matplotlib.pyplot as plt

# print(__package__, __file__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
# create a handler
handler = logging.FileHandler('../DL/maxSim.log' if __package__ == 'DL' else './maxSim.log')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

# 结巴分词库
import jieba
jieba.default_logger.setLevel(logging.ERROR)
# 解析词性
import jieba.posseg as pseg
#绝对路径
def pp(ppath):
	import os
	return os.path.join(os.getcwd(), os.path.dirname(__file__), ppath)
#单个句子类
class Senten2vec():
	def __init__(self,  sentence):
		log.debug('split: %s', sentence.split("#"))
		self.sentence, self.picture = sentence.split('#')
		self.picture = self.picture.strip()
		self.sentence_word = []
		self.sentence_vec = []

	def __str__(self):
		return "sentence%s"%self.sentence + "\nsentence_vec%s\n"%self.sentence_vec
#对链接的处理库
# 链接就是映射句子到图的语句
class link_processor():
	def __init__(self, txt_file='biaoqing.txt', model_file='./fash250.model.bin'):
		self.txt_file = txt_file
		self.model_file = model_file
		self.lastNsen = 6
		with open('/home/ree/data/fashion/attribute.dat', 'rb') as fp:
			import pickle
			self.attr_weigh= pickle.load(fp)
		self.load()

	def load(self):
		from gensim.models import Word2Vec
		# 存放每一个句子实例的库
		self.link_database = []
		# 存放模型
		self.vecmodel = Word2Vec.load(self.model_file)
		log.info('开始载入句子库')
		log.info('开始载入词向量')
		with open(self.txt_file) as fp:
			senten_list = fp.readlines()
			log.debug("senten%s", senten_list)
			for senten_txt in senten_list:
				self.link_database.append(Senten2vec(senten_txt))
		log.info('链接库中的句子分词处理')
		for link in self.link_database:
			link.sentence_word = (set(jieba.cut(link.sentence)))

		for link in self.link_database:
			link.sentence_vec = {word for word in link.sentence_word if word in self.vecmodel.wv.index2word}

		log.info('句子库载入完毕')
	# 找出句子库中相似度最高的n个句子
	def maxSimTxt(self, input_txt='可是', simCondision=0.1):
		if not self.vecmodel:
			self.load()
		for link in  self.link_database:
			link.sim = self.juziSim_vec(input_txt, link.sentence_vec, self.attr_weigh)

		mostNSimlink =sorted(self.link_database, key = lambda link:link.sim, reverse=True)
		log.debug(mostNSimlink)
		log.debug([x.sim for x in self.link_database])
		if len(mostNSimlink)==0 or mostNSimlink[0].sim < simCondision:
			log.info('没有较好匹配的语句，请重新输入其他语句')
			return None
		return mostNSimlink[:self.lastNsen]
	#　输入的语句和单个句子的相似度计算
	def juziSim_vec(self, intxt, questionWordset, posWeight=None):  # juziIn输入的句子，juziLi句子库里的句子
		if posWeight == None:
			log.warning('there is no posWeight')
			return 0
		intxtSet = set(list(pseg.cut(intxt)))
		if not len(intxtSet):
			return 0
		simWeight = 0
		totalWeight = 0
		for word, pos in intxtSet:
			if word in self.vecmodel.wv.index2word:
				wordPosWeight = posWeight.get(pos, 1)
				totalWeight += wordPosWeight

				wordMaxWeight = 0
				for t in questionWordset:
					# print(word, t)
					tmp = self.vecmodel.wv.similarity(word, t)
					if wordMaxWeight < tmp:
						wordMaxWeight = tmp
				simWeight += wordPosWeight * wordMaxWeight
		if totalWeight == 0:
			return 0
		return simWeight/totalWeight

if __name__ == '__main__' :
	log.setLevel(logging.INFO)
	links = link_processor()
	while True:
		try :
			input_sen = input('please input: ')
			mostSim = links.maxSimTxt(input_sen)
			if not mostSim:
				continue
			fig = plt.figure(figsize=(15, 3))
			for i, link in enumerate(mostSim, start=1):
				print('most %d similar sentence is \n%s'%(i, link.sentence))
				log.debug("filename:%s",link.picture)
				img = plt.imread(link.picture)
				plt.subplot(1, links.lastNsen, i)
				plt.imshow(img)
				plt.xticks([]), plt.yticks([])
				plt.title('the most %d similar figure'%i)
			plt.show()
			print('***************%s*******************\n'%input_sen)
		except KeyboardInterrupt as e:
			break

