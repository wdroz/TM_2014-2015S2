# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 13:52:45 2015

@author: droz
"""

import pickle
from os import listdir
from os.path import isfile, join

from pyspark import SparkContext
from FeaturesManager import Features
from DataManager import News

def decode(x):
    news = News()
    news.__dict__ = pickle.load(open(x, 'r'))
    return news
    
if __name__ == "__main__":
    path = '/media/droz/KIKOOLOL HDD/Corpus/pickle/'
    sc = SparkContext()
    onlyfiles = [ join(path,f) for f in listdir(path) if isfile(join(path,f)) ]
    newsRDD = sc.parallelize(onlyfiles).map(decode)
    FeaturesRdd = newsRDD.map(lambda x: Features(x))
    
    nbGood = 0
    nbBad = 0
    filteredFeaturesRDD = FeaturesRdd.filter(lambda x: len(x.getVector()) == 5)
    for feature in  filteredFeaturesRDD.collect():
        print(feature)
        if(feature.isGood()):
            nbGood += 1
        else:
            nbBad += 1
    print("nb good : %d\nnb bad %d" % (nbGood, nbBad))