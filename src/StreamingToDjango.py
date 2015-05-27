# -*- coding: utf-8 -*-
"""
Created on Tue May 26 10:25:48 2015

@author: droz
"""

from os.path import isfile
import pickle
import config
import requests
from ast import literal_eval
import time
import datetime

from pyspark import SparkContext
from GoogleFinanceMarketSource import GoogleFinanceMarketSourceSpark
from ReutersNewsSource import ReutersNewsSourceHDFSV2
from UseFeaturesv2 import DataSetMakerV2
from DataClassifierV2 import DataClassifierMultiClassesOneVsOne
from FeedNewsFromGoogleFinance import FeedNewsFromGoogleFinance

class StreamingToDjango(object):
    def __init__(self, model_name, graph_name):
        self.model = StreamingToDjango.load_model(model_name)
        self.model_name = model_name
        self.graph_name = graph_name
    
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
    
        myList = StreamingToDjango.get_symboles_and_keywords(model_name)        
        symboles = []
        for entry in myList:
            newSource.lookingAll(entry['symboles'][0], entry['keywords'])
            symboles.append(entry['symboles'][0])
        # change by using model symboles and keywords
        
        newsRDD = newSource.doIt()
        marketSource = GoogleFinanceMarketSourceSpark(symboles)
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
        pickle.dump(model, open(model_name, 'wb'), pickle.HIGHEST_PROTOCOL)
        
    @staticmethod    
    def get_streaming_symbole(graph_name):
        '''
        Ask Django for symbole from graph_name for
        streaming
        '''
        try:
            print('try request for symole')
            url = config.DJANGO_CONF['url'] + '/' + config.DJANGO_CONF['streamSymbole'] + '/' + graph_name
            r = requests.get(url)
            myString = str(r.text)
            return myString
        except Exception as e:
            print('exception!!! %s' % str(e))
            return '' # TOTO better error
    
    @staticmethod
    def get_symboles_and_keywords(model_name):
        '''
        Ask Django for symboles and keywords from model_name for
        train a new model.
        '''
        try:
            print('try request for symoles and keywords')
            url = config.DJANGO_CONF['url'] + '/' + config.DJANGO_CONF['trainEntry'] + '/' + model_name
            r = requests.get(url)
            myList = literal_eval(r.text)
            return myList
        except Exception as e:
            print('exception!!! %s' % str(e))
            return [] # TOTO better error
    
    def stream(self):
        
        conf = config.load_spark_conf()
        sc = SparkContext(conf=conf)
        print('stream')
        
        dataSetMaker = DataSetMakerV2(n=config.FEATURES_CONF['vecteur_size'])
        
        feed = FeedNewsFromGoogleFinance()

        model = self.model
        
        def sendRecordToDjango(rdd):
            print('new try...')
            if(not rdd.isEmpty()):
                print('before process')
                newsRDD = dataSetMaker.processKeepNews(rdd)
                print('before res = ')
                res = newsRDD.map(lambda x: (x[0], model.predict(x[1].features)))
                print('afkter res = ')
                print('res size : %d' % res.count())
                print('for each result...')
                for result in res.collect():
                    print('...')
                    symbole = result[0].symbole
                    url = config.DJANGO_CONF['url'] + '/' + config.DJANGO_CONF['addPoint'] + '/' + self.graph_name
                    #newsPubDate=point['newsPubDate'], newsSource=point['newsSource'], newsText=['newsText'], predictScore=point['predictScore'], predictGraph=myPredictGraph
                    myDict = {'newsPubDate' : result[0].pubDate, 'newsSource' : result[0].pubSource, 'newsText' : result[0].publication, 'predictScore' : result[1]}
                    r = requests.post(url, data=myDict)
                    print('send ok')
                    print('receive %s' % str(r.text))
            else:
                print('empty!')
                
        #symboles = ['NASDAQ:GOOGL']
        symboles = [StreamingToDjango.get_streaming_symbole(self.graph_name)]        
        symbolesRDD = sc.parallelize(symboles)
        taskdt = 600
        running = True
        oldNewsRDD = None
        firstTime = True
        intersectRDD = None
        dataDirectory = 'hdfs://157.26.83.52/user/wdroz/stream2'
        cpt = 0
        while(running):
            today = datetime.datetime.now()
            yesterday = today - datetime.timedelta(days=1)
            tomorrow = today + datetime.timedelta(days=1)
            newsRDD = symbolesRDD.flatMap(lambda x: feed.lookingAt(x, yesterday, tomorrow, []))
            if(firstTime):
                firstTime = False
                intersectRDD = newsRDD
            else:
                try:
                    intersectRDD = oldNewsRDD.intersection(newsRDD)
                except:
                    pass # empty rdd
            
            oldNewsRDD = newsRDD
            sendRecordToDjango(intersectRDD)
            try:
                #sendRecordToDjango(intersectRDD)
                print('after send record To django')
                intersectRDD.saveAsPickleFile(dataDirectory + '/' + datetime.datetime.now().strftime('%Y-%m-%d--') + str(cpt))
                cpt += 1
            except Exception as e:
                print('MEGA EXCEPTION!!! %s' % str(e))
                pass # empty rdd
            print('sleep')           
            time.sleep(taskdt)
            print('wake up')
            
        running = True # TODO remove it
        
if __name__ == '__main__':
    stream = StreamingToDjango('Mon premier model','Predict Google')
    stream.stream()