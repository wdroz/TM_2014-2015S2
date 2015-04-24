# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 12:28:00 2015

@author: droz
"""


from DataClassifier import DataClassifier, DataClassifierEvaluator
from DataClassifierV2 import ClassifiersWrapper, DecisionTreeWrapper, DataClassifierMultiClassesOneVsOne, DataClassifierMultiClassesOneVsMany
from pyspark.mllib.classification import SVMWithSGD, LogisticRegressionWithSGD, LogisticRegressionWithLBFGS, NaiveBayes
from pyspark.mllib.tree import DecisionTree
from MessageManager import MessageManager
from UseFeaturesv2 import DataSetMakerV2
from ReutersNewsSource import ReutersNewsSourceHDFSV2
from pyspark import SparkContext, SparkConf
from GoogleFinanceMarketSource import GoogleFinanceMarketSourceSpark
import pickle

if __name__ == "__main__":
    conf = SparkConf()
    conf.set('spark.shuffle.blockTransferService', 'nio')
    conf.set('spark.files.fetchTimeout', '180')
    conf.set('spark.files.overwrite', 'yes')
    conf.set('spark.akka.timeout', '180')
    conf.set('spark.task.maxFailures', '30000')
    conf.set('spark.akka.frameSize', '500')
    conf.set('spark.network.timeout', '180')
    #conf.set('spark.executor.memory', '6g')
    #conf.set('spark.shuffle.memoryFraction', "0")
    sc = SparkContext(conf=conf)
    
    path = 'hdfs://157.26.83.52/user/wdroz/headlines-docs.csv'    
    fileRdd = sc.textFile(path, use_unicode=False)
    newSource = ReutersNewsSourceHDFSV2(fileRdd)

    newSource.lookingAll('NASDAQ:GOOGL', ['GOOG', 'GOOGL', 'GOOGLE'])
    newSource.lookingAll('NASDAQ:NVDA', ['NVIDIA'])
    newSource.lookingAll('VTX:NESN', ['NESTLE'])
    newSource.lookingAll('VTX:SCMN', ['SWISSCOM'])
    newSource.lookingAll('VTX:NOVN', ['NOVARTIS'])
    
    newsRDD = newSource.doIt()
    marketSource = GoogleFinanceMarketSourceSpark(['NASDAQ:GOOGL', 'NASDAQ:NVDA', 'VTX:NESN', 'VTX:SCMN', 'VTX:NOVN'])
    newsRDD = newsRDD.map(lambda x: marketSource.addMarketStatusToNews(x))
    
    #newsRDD = newsRDD.randomSplit([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])[0]
    newsRDD.cache()
    print('nb news : %d' % newsRDD.count())
    dataSetMaker = DataSetMakerV2(n=200000)
    fullDataSet = dataSetMaker.process(newsRDD)
    #fullDataSet.cache()
    #newsRDD = newsRDD.randomSplit([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])[0]
    toto = fullDataSet.take(1)[0]
    
    myClassifierOnevsOne = pickle.load(open('myClassifierOnevsOne.p','rb'))
    
    
    
    pred = myClassifierOnevsOne.predict(toto.features)
    print('pred is : %d reality is %d' % (pred, toto.label))
    
    

