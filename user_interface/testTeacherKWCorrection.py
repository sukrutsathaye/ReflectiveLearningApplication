# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 19:13:48 2021

@author: sukru
"""
import pickle
import os
import pprint

path = 'D:\Student Arbeit\Latest Code 0803\Topics\Black Hole'

checked = os.path.join(path, 'questions.pkl')
with open(checked, 'rb') as f:
    ckw = pickle.load(f)
# print("checked: ", ckw)
# unchecked = os.path.join(path, 'unchecked_kw.pkl')
# with open(unchecked, 'rb') as f:
#     unckw = pickle.load(f)
# print("Unchecked: ", len(unckw))
pprint.pprint(ckw[0],indent=2,depth=2, width=300)