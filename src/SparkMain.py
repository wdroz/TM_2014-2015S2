# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 13:52:45 2015

@author: droz
"""

import pickle
from os import listdir
from os.path import isfile, join

from pyspark import SparkContext

def decode(x):
    return pickle.load(open(x, 'r'))
if __name__ == "__main__":
    path = '/media/droz/KIKOOLOL HDD/Corpus/pickle/'
    sc = SparkContext()
    onlyfiles = [ join(path,f) for f in listdir(path) if isfile(join(path,f)) ]
    newsRDD = sc.parallelize(onlyfiles).map(decode)
    for new in newsRDD.collect():
        print(str(new))