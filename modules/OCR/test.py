#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-05-30 22:20:08
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import pickle
import re

if __name__ == '__main__':
    source = '宫颈癌；旅顺口打飞_马'
    test_dict = {}
    test_dict['_'] = '一'
    with open('substitude.dat' , 'wb') as fp:
        pickle.dump(test_dict, fp, 1)
    with open('substitude.dat', 'rb') as fp:
        rec = pickle.load(fp)
    keys = rec.keys()
    for key in keys:
        if key in source:
            print(re.subn(key, rec[key], source))
    print(rec)

