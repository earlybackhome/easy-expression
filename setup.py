#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-05-30 11:46:41
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import sys
import logging
import os

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

#sys.path.append('modules/')
#from modules.DL import maxSim
#from modules.OCR import Image2txt

if __name__ == '__main__':
	dependencies = ['matplotlib', 'cv2', 'jieba', 'pyocr', 'numpy', 'sklearn', 'PIL']
	print('Before we run the core,  we need these package preinstalled\n%s',
		 dependencies)
	uninstall = []
	for package in dependencies:
		try:
			print('checking %s ...'%package)
			__import__(package)
		except ImportError as e:
			uninstall.append(package)
			log.info('ImportError %s', e)
		else:
			print('successfully imported %s'%package)
	if len(uninstall) == 0:
		os.chdir('./modules/QQqt4/')
		os.system('python3  pyqtChatApp.py')
	else :
		print('Please install these packages:\n %s'%uninstall)
