# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 14:24:01 2015

@author: droz
"""
'''
import os
os.environ['HOME'] = '/tmp'
os.environ['SPARK_WORKER_DIR'] = '/tmp'
'''
from DataClassifier import DataClassifier
from pyspark.mllib.classification import SVMWithSGD, LogisticRegressionWithSGD, LogisticRegressionWithLBFGS
from MessageManager import MessageManager
from UseFeaturesv2 import DataSetMakerV2
from ReutersNewsSource import ReutersNewsSourceHDFS
from pyspark import SparkContext, SparkConf
from GoogleFinanceMarketSource import GoogleFinanceMarketSourceSpark
if __name__ == "__main__":
    conf = SparkConf()
    #conf.set('spark.shuffle.memoryFraction', "0")
    sc = SparkContext()
    #path = '/media/droz/KIKOOLOL HDD/Corpus/headlines-docs.csv'
    path = 'hdfs://157.26.83.52/user/wdroz/headlines-docs.csv'    
    fileRdd = sc.textFile(path, use_unicode=False)
    newSource = ReutersNewsSourceHDFS(fileRdd)
    newsRDD1 = newSource.lookingAll('NASDAQ:GOOGL', ['GOOG', 'GOOGL', 'GOOGLE'])
    #newsRDD2 = newSource.lookingAll('NASDAQ:NVDA', ['NVIDIA'])
    #newsRDD = newsRDD1.union(newsRDD2)
    newsRDD = newsRDD1    
    marketSource = GoogleFinanceMarketSourceSpark(['NASDAQ:GOOGL'])
    newsRDD = newsRDD.map(lambda x: marketSource.addMarketStatusToNews(x))
    newsRDD.cache()
    print('nb news : %d' % newsRDD.count())
    dataSetMaker = DataSetMakerV2(n=200000)
    fullDataSet = dataSetMaker.process(newsRDD)
    fullDataSet.cache()
    dc = DataClassifier(fullDataSet, LogisticRegressionWithLBFGS)
    MessageManager.debugMessage("main : start crossvalidation")
    precMin, precMax, prec = dc.crossvalidation(5)
    print('min : %f, max : %f, mean : %f' % (precMin, precMax, prec))
    
    