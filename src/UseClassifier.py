# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 13:35:55 2015

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

if __name__ == "__main__":
    conf = SparkConf()
    #conf.set('spark.shuffle.memoryFraction', "0")
    sc = SparkContext()
    #toto = DataClassifierMultiClasses(SVMWithSGD, 5)
    #path = '/media/droz/KIKOOLOL HDD/Corpus/headlines-docs.csv'
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
    fullDataSet.cache()
    myClassifier = ClassifiersWrapper()
    myClassifier.addClassifier(classifier=SVMWithSGD, trainParameters={}, weight=0.3)
    myClassifier.addClassifier(classifier=LogisticRegressionWithSGD, trainParameters={}, weight=0.3)
    myClassifier.addClassifier(classifier=NaiveBayes, trainParameters={}, weight=0.3)
    myClassifier.addClassifier(classifier=LogisticRegressionWithLBFGS, trainParameters={}, weight=0.7)
    
    myClassifier2 = ClassifiersWrapper()
    myClassifier2.addClassifier(classifier=SVMWithSGD, trainParameters={}, weight=0.3)
    myClassifier2.addClassifier(classifier=LogisticRegressionWithSGD, trainParameters={}, weight=0.3)
    myClassifier2.addClassifier(classifier=NaiveBayes, trainParameters={}, weight=0.3)
    myClassifier2.addClassifier(classifier=LogisticRegressionWithLBFGS, trainParameters={}, weight=0.7)
    
    dataClassifierEvaluator = DataClassifierEvaluator(fullDataSet)
    #dataClassifierEvaluator.addModel(myClassifier, 'My Classifier')
    myClassifierOnevsOne = DataClassifierMultiClassesOneVsOne(myClassifier, 4)
    myClassifierOnevsMany = DataClassifierMultiClassesOneVsMany(myClassifier2, 4)
    dataClassifierEvaluator.addModel(myClassifierOnevsMany, 'myClassifierOnevsMany')
    dataClassifierEvaluator.addModel(myClassifierOnevsOne, 'myClassifierOnevsOne')
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