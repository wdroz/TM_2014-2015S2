# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 13:52:45 2015

@author: droz
"""

import pickle
from os import listdir
from os.path import isfile, join
from random import shuffle
from textblob.classifiers import NaiveBayesClassifier
from DataAnalyser import DataAnalyzerLocal

from pyspark import SparkContext
from FeaturesManager import Features
from DataManager import News

def decode(x):
    news = News()
    news.__dict__ = pickle.load(open(x, 'r'))
    return news
    
if __name__ == "__main__":
    path = '/home/droz/data/'
    sc = SparkContext()
    onlyfiles = [ join(path,f) for f in listdir(path) if isfile(join(path,f)) ]
    newsRDD = sc.parallelize(onlyfiles).map(decode)
    featuresRdd = newsRDD.map(lambda x: Features(x))
    dataAnalyser = DataAnalyzerLocal()
    #featuresRdd.foreach(lambda x: dataAnalyser.addFeature(x))
    f = featuresRdd.collect()
    [dataAnalyser.addFeature(x) for x in f]    
    dataAnalyser.plot()
    #for x in f:
    #    print(str(x))
    '''
    
    nbGood = 0
    nbBad = 0
    filteredFeaturesRDD = FeaturesRdd.filter(lambda x: len(x.getVector()) == 5)
    dataSetRDD = filteredFeaturesRDD.map(lambda x: x.getPairforClassification())    
    dataSetTab = dataSetRDD.collect()
    shuffle(dataSetTab)
    nbRec = len(dataSetTab)
    train = dataSetTab[:int(0.8*nbRec)]
    test = dataSetTab[int(0.8*nbRec):]
    cl = NaiveBayesClassifier(train)
    accuracy = cl.accuracy(test)
    print('accuracy : %f' % accuracy)
    '''
    '''
    for feature in  filteredFeaturesRDD.collect():
        print(feature)
        if(feature.isGood()):
            nbGood += 1
        else:
            nbBad += 1
    print("nb good : %d\nnb bad %d" % (nbGood, nbBad))'''