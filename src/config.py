# -*- coding: utf-8 -*-
"""
Created on Tue May 26 13:34:40 2015

@author: droz
"""

FEATURES_CONF = {
    'hdfs' : 'hdfs://157.26.83.52',
    'headlines' : 'user/wdroz/headlines-docs.csv',
    'vecteur_size' : 200000,
    'nb_classes' : 4,
}

DJANGO_CONF = {
    'url' : 'http://127.0.0.1:8000',
    'addPoint' : 'addPoint',
    'trainStatus' : 'trainStatus',
    'streamStatus' : 'streamStatus',
}

def load_spark_conf():
    from pyspark import SparkConf
    conf = SparkConf()
    conf.set('spark.files.fetchTimeout', '180')
    conf.set('spark.files.overwrite', 'yes')
    conf.set('spark.akka.timeout', '180')
    conf.set('spark.task.maxFailures', '30000')
    conf.set('spark.akka.frameSize', '500')
    conf.set('spark.network.timeout', '180')
    return conf
    
def load_best_classifier_conf():
    from DataClassifierV2 import ClassifiersWrapper
    from pyspark.mllib.classification import SVMWithSGD, LogisticRegressionWithSGD, LogisticRegressionWithLBFGS, NaiveBayes
    myClassifier = ClassifiersWrapper()
    myClassifier.addClassifier(classifier=SVMWithSGD, trainParameters={}, weight=0.3)
    myClassifier.addClassifier(classifier=LogisticRegressionWithSGD, trainParameters={}, weight=0.3)
    myClassifier.addClassifier(classifier=NaiveBayes, trainParameters={}, weight=0.3)
    myClassifier.addClassifier(classifier=LogisticRegressionWithLBFGS, trainParameters={}, weight=0.7)
    return myClassifier