# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 14:24:01 2015

@author: droz

DO NOT USE - DEPRECIATED

"""
'''
import os
os.environ['HOME'] = '/tmp'
os.environ['SPARK_WORKER_DIR'] = '/tmp'
'''
from DataClassifier import DataClassifier, DataClassifierEvaluator
from DataClassifierV2 import ClassifiersWrapper, DecisionTreeWrapper, DataClassifierMultiClasses
from pyspark.mllib.classification import SVMWithSGD, LogisticRegressionWithSGD, LogisticRegressionWithLBFGS, NaiveBayes
from pyspark.mllib.tree import DecisionTree
from MessageManager import MessageManager
from UseFeaturesv2 import DataSetMakerV2
from ReutersNewsSource import ReutersNewsSourceHDFSV2
from pyspark import SparkContext, SparkConf
from GoogleFinanceMarketSource import GoogleFinanceMarketSourceSpark
if __name__ == "__main__":
    conf = SparkConf()
    #conf.set('spark.shuffle.memoryFraction', "0")
    sc = SparkContext()
    #toto = DataClassifierMultiClasses(SVMWithSGD, 5)
    #path = '/media/droz/KIKOOLOL HDD/Corpus/headlines-docs.csv'
    path = 'hdfs://157.26.83.52/user/wdroz/mini-headlines-docs.csv'    
    fileRdd = sc.textFile(path, use_unicode=False)
    newSource = ReutersNewsSourceHDFSV2(fileRdd)
    #newsRDD1 = newSource.lookingAll('NASDAQ:GOOGL', ['GOOG', 'GOOGL', 'GOOGLE'])
    #newsRDD2 = newSource.lookingAll('NASDAQ:NVDA', ['NVIDIA'])
    #newsRDD3 = newSource.lookingAll('VTX:NESN', ['NESTLE'])
    #newsRDD4 = newSource.lookingAll('VTX:SCMN', ['SWISSCOM'])
    #newsRDD5 = newSource.lookingAll('VTX:NOVN', ['NOVARTIS'])  
    #newsRDD = newsRDD1.union(newsRDD2)
    #newsRDD = newsRDD1.union(newsRDD2).union(newsRDD3).union(newsRDD4).union(newsRDD5)
    #newsRDD = newsRDD4
    newSource.lookingAll('NASDAQ:GOOGL', ['GOOG', 'GOOGL', 'GOOGLE'])
    newSource.lookingAll('NASDAQ:NVDA', ['NVIDIA'])
    newSource.lookingAll('VTX:NESN', ['NESTLE'])
    newSource.lookingAll('VTX:SCMN', ['SWISSCOM'])
    newSource.lookingAll('VTX:NOVN', ['NOVARTIS'])
    
    newsRDD = newSource.doIt()
    marketSource = GoogleFinanceMarketSourceSpark(['NASDAQ:GOOGL', 'NASDAQ:NVDA', 'VTX:NESN', 'VTX:SCMN', 'VTX:NOVN'])
    newsRDD = newsRDD.map(lambda x: marketSource.addMarketStatusToNews(x))
    newsRDD.cache()
    print('nb news : %d' % newsRDD.count())
    dataSetMaker = DataSetMakerV2(n=200000)
    fullDataSet = dataSetMaker.process(newsRDD)
    fullDataSet.cache()
    myClassifier = ClassifiersWrapper()
    myClassifier.addClassifier(classifier=SVMWithSGD, trainParameters={}, weight=0.3)
    myClassifier.addClassifier(classifier=LogisticRegressionWithSGD, trainParameters={}, weight=0.3)
    myClassifier.addClassifier(classifier=NaiveBayes, trainParameters={}, weight=0.3)
    myClassifier.addClassifier(classifier=LogisticRegressionWithLBFGS, trainParameters={}, weight=0.7)
    dataClassifierEvaluator = DataClassifierEvaluator(fullDataSet)
    #dataClassifierEvaluator.addModel(myClassifier, 'My Classifier')
    dataClassifierEvaluator.addModel(NaiveBayes, 'NaiveBayes')
    #tree = DecisionTreeWrapper(classifier=DecisionTree, trainParameters={'numClasses': 4, 'categoricalFeaturesInfo' : {}})
    #dataClassifierEvaluator.addModel(tree, 'DecisionTreeWrapper')
    #dataClassifierEvaluator.addModel(LogisticRegressionWithLBFGS, 'LogisticRegressionWithLBFGS')
    #dataClassifierEvaluator.addModel(SVMWithSGD, 'SVMWithSGD')
    dataClassifierEvaluator.crossvalidation()
    #dataClassifierEvaluator.selectBestModel()
    #dc = DataClassifier(fullDataSet, LogisticRegressionWithLBFGS)
    #MessageManager.debugMessage("main : start crossvalidation")
    #precMin, precMax, prec = dc.crossvalidation(5)
    #print('min : %f, max : %f, mean : %f' % (precMin, precMax, prec))
    
    