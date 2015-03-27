# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 13:52:45 2015

@author: droz
"""

import pickle
from MessageManager import MessageManager
from DataClassifier import DataClassifier

from pyspark import SparkContext, SparkConf
from DataManager import News
from pyspark.mllib.classification import SVMWithSGD

from ast import literal_eval
from pyspark.mllib.regression import LabeledPoint

def decode(x):
    news = News()
    news.__dict__ = pickle.load(open(x, 'r'))
    return news

def reUseDataClassifier():
    dc = DataClassifier(None, SVMWithSGD)
    dc.loadModel()

    
def useDataClassifier(filepath='/media/droz/KIKOOLOL HDD/Corpus/dataset/dataset.txt', sc=None):
    MessageManager.debugMessage("useDataClassifier : start open file %s" % filepath)
    lines = sc.textFile(filepath)
    fullDataSet = lines.map(lambda line: literal_eval(line)).map(lambda (data,label): LabeledPoint((1 if label else 0), data))
    fullDataSet.cache()
    #fullDataSet = sc.parallelize(fullDataSet)
    dc = DataClassifier(fullDataSet, SVMWithSGD)
    MessageManager.debugMessage("useDataClassifier : start crossvalidation")
    precMin, precMax, prec = dc.crossvalidation(5)
    print('min : %f, max : %f, mean : %f' % (precMin, precMax, prec))
    MessageManager.debugMessage("useDataClassifier : train full dataset")
    dc.train(fullDataSet)
    dc.saveModel()
    
def classification(filepath='/media/droz/KIKOOLOL HDD/Corpus/dataset/dataset.txt', sc=None):
    MessageManager.debugMessage("classification : start open file %s" % filepath)
    lines = sc.textFile(filepath)
    fullDataSet = lines.map(lambda line: literal_eval(line)).map(lambda (data,label): LabeledPoint((1 if label else 0), data)).cache()
    MessageManager.debugMessage("classification : start split dataset")
    trainRdd, testRdd = fullDataSet.randomSplit([80,20], 17)
    dc = DataClassifier()
    MessageManager.debugMessage("classification : start training")
    dc.train(trainRdd)
    MessageManager.debugMessage("classification : stop training")
    MessageManager.debugMessage("classification : start prediction")
    evaluatorRdd = testRdd.map(lambda p: (p.label, dc.predict(p.features)))
    nbOK = evaluatorRdd.filter(lambda (a, b): a == b).count()
    nbTOT = testRdd.count()
    precision = nbOK/float(nbTOT)
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
    #classification(sc=sc)
    useDataClassifier(filepath='hdfs://157.26.83.52/user/wdroz/dataset.txt', sc=sc)     
    
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