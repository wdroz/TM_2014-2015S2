# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 14:24:01 2015

@author: droz
"""
import os
os.environ['HOME'] = '/tmp'
os.environ['SPARK_WORKER_DIR'] = '/tmp'

from DataClassifier import DataClassifier
from pyspark.mllib.classification import SVMWithSGD
from MessageManager import MessageManager
from UseFeaturesv2 import DataSetMaker
from ReutersNewsSource import ReutersNewsSourceHDFS
from pyspark import SparkContext, SparkConf

if __name__ == "__main__":
    conf = SparkConf()
    #conf.set('spark.shuffle.memoryFraction', "0")
    sc = SparkContext()
    #path = '/media/droz/KIKOOLOL HDD/Corpus/headlines-docs.csv'
    path = 'hdfs://157.26.83.52/user/wdroz/headlines-docs.csv'    
    fileRdd = sc.textFile(path, use_unicode=False)
    newSource = ReutersNewsSourceHDFS(fileRdd)
    newsRDD = newSource.lookingAll('NASDAQ:GOOGL', ['GOOG', 'GOOGL', 'GOOGLE'])
    newsRDD.cache()
    print('nb news : %d' % newsRDD.count())
    dataSetMaker = DataSetMaker()
    dataSetMaker.process(newsRDD)
    fullDataSet = dataSetMaker.vectorize()
    fullDataSet.cache()
    dc = DataClassifier(fullDataSet, SVMWithSGD)
    MessageManager.debugMessage("main : start crossvalidation")
    precMin, precMax, prec = dc.crossvalidation(5)
    print('min : %f, max : %f, mean : %f' % (precMin, precMax, prec))
    
    