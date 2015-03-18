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
from TextToVect import TextToVectSpark
from MessageManager import MessageManager
from DataClassifier import DataClassifier

from pyspark import SparkContext, SparkConf
from FeaturesManager import Features
from DataManager import News

from ast import literal_eval
from pyspark.mllib.regression import LabeledPoint

def decode(x):
    news = News()
    news.__dict__ = pickle.load(open(x, 'r'))
    return news
    
def classification(filepath='/media/droz/KIKOOLOL HDD/Corpus/dataset/dataset.txt', sc=None):
    labelledPoints = []
    MessageManager.debugMessage("classification : start open file %s" % filepath)
    nb_max_cheat = 500
    cpt=0
    with open(filepath, 'r') as f:
        for line in f:
            cpt += 1
            myTuple = literal_eval(line)
            labelledPoints.append(LabeledPoint((1 if myTuple[1] else 0), myTuple[0]))
            if(cpt >= nb_max_cheat): # cheat because fuck memory
                break
    MessageManager.debugMessage("classification : start shuffle")
    shuffle(labelledPoints)    
    MessageManager.debugMessage("classification : close file %s" % filepath)    
    nbRec = len(labelledPoints)
    MessageManager.debugMessage("classification : start split dataset")
    train = labelledPoints[:int(0.8*nbRec)]
    MessageManager.debugMessage("classification : train set len : %d" % len(train))
    test = labelledPoints[int(0.8*nbRec):]
    MessageManager.debugMessage("classification : test set len : %d" % len(test))
    trainRdd = sc.parallelize(train)
    #testRdd = sc.parallelize(test)
    dc = DataClassifier()
    MessageManager.debugMessage("classification : start training")
    dc.train(trainRdd)
    MessageManager.debugMessage("classification : stop training")
    nbOK = 0
    nbKO = 0
    MessageManager.debugMessage("classification : start prediction")
    for p in test:
        res = dc.predict(p.features)
        if(res == p.label):
            nbOK += 1
        else:
            nbKO += 1
    MessageManager.debugMessage("classification : stop prediction")
    precision = nbOK/float(nbKO + nbOK)
    print('precision : %f' % precision)
    
    
if __name__ == "__main__":
    path = '/home/droz/data/'
    conf = SparkConf()
    #conf.set("spark.executor.memory", "4g")
    sc = SparkContext(conf=conf)
    #onlyfiles = [ join(path,f) for f in listdir(path) if isfile(join(path,f)) ]
    #newsRDD = sc.parallelize(onlyfiles).map(decode)
    #featuresRdd = newsRDD.map(lambda x: Features(x))
    #ttv = TextToVectSpark(1)
    #res = ttv.vectorize(featuresRdd)
    classification(sc=sc)
            
    
    #for x in res:
    #    print('vector len : %d, %s' % (x[0], str(x[1])))
   # dataAnalyser = DataAnalyzerLocal()
    #featuresRdd.foreach(lambda x: dataAnalyser.addFeature(x))
    #f = featuresRdd.collect()
    #[dataAnalyser.addFeature(x) for x in f]    
    #dataAnalyser.plot()
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