# -*- coding: utf-8 -*-
"""
Created on Fri May  8 09:02:19 2015

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

import matplotlib.pyplot as plt
import numpy as np

def plot_confusion_matrix(cm, title='Confusion matrix', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(cm))
    plt.xticks(tick_marks, list(range(len(cm))), rotation=45)
    plt.yticks(tick_marks, list(range(len(cm))))
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()


if __name__ == "__main__":
    #cm = [[71,2,3,7],[8,70,1,3],[8,1,24,3], [12,4,0,70]]
    #plot_confusion_matrix(cm)
    
    conf = SparkConf()
    #conf.set('spark.shuffle.blockTransferService', 'nio')
    conf.set('spark.files.fetchTimeout', '180')
    conf.set('spark.files.overwrite', 'yes')
    conf.set('spark.akka.timeout', '180')
    conf.set('spark.task.maxFailures', '30000')
    conf.set('spark.akka.frameSize', '500')
    conf.set('spark.network.timeout', '180')
    #conf.set('spark.executor.memory', '6g')
    #conf.set('spark.shuffle.memoryFraction', "0")
    sc = SparkContext(conf=conf)
    #toto = DataClassifierMultiClasses(SVMWithSGD, 5)
    #path = '/media/droz/KIKOOLOL HDD/Corpus/headlines-docs.csv'
    path = 'hdfs://157.26.83.52/user/wdroz/tail-headlines-docs.csv'    
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
    #dataClassifierEvaluator.addModel(myClassifierOnevsMany, 'myClassifierOnevsMany')
    dataClassifierEvaluator.addModel(myClassifierOnevsOne, 'myClassifierOnevsOne')
    #dataClassifierEvaluator.addModel(NaiveBayes, 'NaiveBayes')
    #tree = DecisionTreeWrapper(classifier=DecisionTree, trainParameters={'numClasses': 4, 'categoricalFeaturesInfo' : {}})
    #dataClassifierEvaluator.addModel(tree, 'DecisionTreeWrapper')
    #dataClassifierEvaluator.addModel(LogisticRegressionWithLBFGS, 'LogisticRegressionWithLBFGS')
    #dataClassifierEvaluator.addModel(SVMWithSGD, 'SVMWithSGD')
    dataClassifierEvaluator.crossvalidation(nbSplits=2)
    plot_confusion_matrix(dataClassifierEvaluator.matrixConfusion)
    #dataClassifierEvaluator.selectBestModel()
    #dc = DataClassifier(fullDataSet, LogisticRegressionWithLBFGS)
    #MessageManager.debugMessage("main : start crossvalidation")
    #precMin, precMax, prec = dc.crossvalidation(5)
    #print('min : %f, max : %f, mean : %f' % (precMin, precMax, prec))




