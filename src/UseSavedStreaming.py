# -*- coding: utf-8 -*-
"""
Created on Mon May  4 10:00:42 2015

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
from pyspark.streaming import StreamingContext
from DataManager import News
import pickle
import requests
from ast import literal_eval
import datetime        
from collections import defaultdict
from PredictionsHandlerFlask import NewsPrediction
import json

if __name__ == "__main__":
    conf = SparkConf()
    #conf.set('spark.shuffle.blockTransferService', 'nio')
    conf.set('spark.files.fetchTimeout', '180')
    conf.set('spark.files.overwrite', 'yes')
    conf.set('spark.akka.timeout', '180')
    conf.set('spark.task.maxFailures', '30000')
    conf.set('spark.akka.frameSize', '500')
    conf.set('spark.network.timeout', '180')
    
    dataDirectory = 'hdfs://157.26.83.52/user/wdroz/stream2'
    
    myClassifierOnevsOne = pickle.load(open('myClassifierOnevsOne.p','rb'))
    
    dataSetMaker = DataSetMakerV2(n=200000)
    
    sc = SparkContext(conf=conf)

    
    newsRDD = sc.pickleFile(dataDirectory + '/2015-05-040')
    
    print('%d news' % newsRDD.count())
    
    for news in newsRDD.collect():
        try:
            print(str(news))
        except:
            pass
    