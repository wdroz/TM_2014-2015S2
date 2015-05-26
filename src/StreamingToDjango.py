# -*- coding: utf-8 -*-
"""
Created on Tue May 26 10:25:48 2015

@author: droz
"""

from os.path import isfile
import pickle
import config
from pyspark import SparkContext
from GoogleFinanceMarketSource import GoogleFinanceMarketSourceSpark
from ReutersNewsSource import ReutersNewsSourceHDFSV2
from UseFeaturesv2 import DataSetMakerV2
from DataClassifierV2 import DataClassifierMultiClassesOneVsOne

class StreamingToDjango(object):
    def __init__(self, model_name, graph_name):
        self.model = StreamingToDjango.load_model(model_name)
    
    @staticmethod
    def load_model(model_name):
        if(StreamingToDjango.check_if_model_exist(model_name)):
            return pickle.load(open(model_name, 'rb'))
        else:
            model = StreamingToDjango.create_model(model_name)
            StreamingToDjango.save_model(model_name, model)
            return model
            
    
    @staticmethod
    def check_if_model_exist(model_name):
        return isfile(model_name)
    
    @staticmethod
    def create_model(model_name):
        '''
        Train a new model
        '''
        conf = config.load_spark_conf()
        sc = SparkContext(conf=conf)
        path = config.FEATURES_CONF['hdfs'] + '/' + config.FEATURES_CONF['headlines']
        #path = 'hdfs://157.26.83.52/user/wdroz/headlines-docs.csv'    
        fileRdd = sc.textFile(path, use_unicode=False)
        newSource = ReutersNewsSourceHDFSV2(fileRdd)
    
        # change by using model symboles and keywords
        newSource.lookingAll('NASDAQ:GOOGL', ['GOOG', 'GOOGL', 'GOOGLE'])
        newSource.lookingAll('NASDAQ:NVDA', ['NVIDIA'])
        newSource.lookingAll('VTX:NESN', ['NESTLE'])
        newSource.lookingAll('VTX:SCMN', ['SWISSCOM'])
        newSource.lookingAll('VTX:NOVN', ['NOVARTIS'])
        
        newsRDD = newSource.doIt()
        marketSource = GoogleFinanceMarketSourceSpark(['NASDAQ:GOOGL', 'NASDAQ:NVDA', 'VTX:NESN', 'VTX:SCMN', 'VTX:NOVN'])
        newsRDD = newsRDD.map(lambda x: marketSource.addMarketStatusToNews(x))
        #newsRDD = newsRDD.randomSplit([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])[0]
        # send reading corpus and add marketStatus
        newsRDD.cache()
        print('nb news : %d' % newsRDD.count())
        dataSetMaker = DataSetMakerV2(n=config.FEATURES_CONF['vecteur_size'])
        fullDataSet = dataSetMaker.process(newsRDD)
        fullDataSet.cache()
        
        myClassifier = config.load_best_classifier_conf()
    
        
        myClassifierOnevsOne = DataClassifierMultiClassesOneVsOne(myClassifier, config.FEATURES_CONF['nb_classes'])
        print('train')
        myClassifierOnevsOne.train(fullDataSet)
        print('stop')
        sc.stop() # terminate spark context
        
        return myClassifierOnevsOne
    
    @staticmethod
    def save_model(model_name, model):
        pickle.dump(model, open(model_name, 'wb'))
    
    @staticmethod
    def get_symboles_and_keywords(model_name):
        '''
        Ask Django for symboles and keywords from model_name for
        train a new model.
        '''
        pass
    
    def stream(self):
        conf = config.load_spark_conf()
        sc = SparkContext(conf=conf)
        print('stream')
        # TODO stream
        
if __name__ == '__main__':
    stream = StreamingToDjango('abc','def')
    stream.stream()