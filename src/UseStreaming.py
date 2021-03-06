# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 13:02:54 2015

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
    
    dataDirectory = 'hdfs://157.26.83.52/user/wdroz/stream'
    
    myClassifierOnevsOne = pickle.load(open('myClassifierOnevsOne.p','rb'))
    
    dataSetMaker = DataSetMakerV2(n=200000)
    
    sc = SparkContext(conf=conf)

    ssc = StreamingContext(sc, batchDuration=20)
    
    text = ssc.textFileStream(dataDirectory)
    
    
    
    dicoRDD = text.map(lambda x: literal_eval(x))
    
    newTRDD = dicoRDD.map(lambda x: News(pubDate=datetime.datetime.now(), symbole='NASDAQ:GOOGL', publication=x['text'], pubSource=x['source'], marketStatus=[]))
    
    def sendRecord(rdd):
        print('new try...')
        if(not rdd.isEmpty()):
            newsRDD = dataSetMaker.processKeepNews(rdd)
            res = newsRDD.map(lambda x: (x[0], myClassifierOnevsOne.predict(x[1].features)))
            print('for each result...')
            for result in res.collect():
                symbole = result[0].symbole
                r = requests.put('http://localhost:5000', data={'jdata' : NewsPrediction(result[0], str(result[1])).json(),  'symbole' : symbole, 'label' : str(result[1])})
                print('send ok')
                print('receive %s' % str(r.text))
        else:
            print('empty!')
    
    newTRDD.foreachRDD(sendRecord)
    
    newTRDD.foreachRDD(lambda x: sendRecord(x))
    
    ssc.start()
    ssc.awaitTermination()
    