# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 13:27:05 2015

@author: droz
"""

import HTMLParser
import re
import requests
import datetime

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
import time

class FeedNewsfromGoogleFinance(object):
    def __init__(self):
        self.url = 'https://www.google.com/finance/company_news'
        self.expNews = '<div style="width:100%;">([^/]+)</div>'
        self.expDate = '<span class=date>([^/]+)</span>'
        self.expPubSource = '<span class=src>([^/]+)</span>'
        self.num = 10
        self.h = HTMLParser.HTMLParser()
        
    def lookingAt(self, symbole, startDate, endDate, keywords):
        recentNews = []
        hasMoreQuote=True
        params = {'q' : symbole, 'startdate' : str(startDate.strftime('%Y-%m-%d')), 'enddate' : str(endDate.strftime('%Y-%m-%d')), 'start' : 0, 'num' : self.num}
        while(hasMoreQuote):
            print('requests with %s' % str(params))
            r = requests.get(self.url, params=params)
            print('requests code %d' % r.status_code)
            #print('content %s' % r.content)
            text = self.h.unescape(r.text).encode('utf-8')
            quotes = re.findall(self.expNews, text)  
            dates = re.findall(self.expDate, text)
            sources = re.findall(self.expPubSource, text)
            if(len(quotes) < self.num):
                hasMoreQuote=False
            for cpt in xrange(len(quotes)):
                try:
                    #Feb 26, 2015
                    date = datetime.datetime.strptime(dates[cpt], "%b %d, %Y")
                    recentNews.append(News(pubDate=date, symbole=symbole, publication=quotes[cpt], pubSource=sources[cpt]))
                    print('sources : %s' % sources)
                except:
                    recentNews.append(News(pubDate=datetime.datetime.now(), symbole=symbole, publication=quotes[cpt], pubSource=sources[cpt]))
            params['start'] += self.num
            
        return recentNews

def run():
    conf = SparkConf()
    #conf.set('spark.shuffle.blockTransferService', 'nio')
    conf.set('spark.files.fetchTimeout', '180')
    conf.set('spark.files.overwrite', 'yes')
    conf.set('spark.akka.timeout', '180')
    #conf.set('spark.task.maxFailures', '30000')
    conf.set('spark.akka.frameSize', '500')
    conf.set('spark.network.timeout', '180')
    
    myClassifierOnevsOne = pickle.load(open('myClassifierOnevsOne.p','rb'))
    
    dataSetMaker = DataSetMakerV2(n=200000)
    
    feed = FeedNewsfromGoogleFinance()
    
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
    
    sc = SparkContext(conf=conf)
    
    symbolesRDD = sc.parallelize([('NASDAQ:GOOGL', ['GOOG', 'GOOGL', 'GOOGLE']), ('NASDAQ:NVDA', ['NVIDIA']), ('VTX:SCMN', ['SWISSCOM'])])
    taskdt = 600
    running = True
    oldNewsRDD = None
    firstTime = True
    intersectRDD = None
    dataDirectory = 'hdfs://157.26.83.52/user/wdroz/stream2'
    while(running):
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        newsRDD = symbolesRDD.flatMap(lambda x: feed.lookingAt(x[0], today, tomorrow, x[1]))
        if(firstTime):
            firstTime = False
            intersectRDD = newsRDD
        else:
            try:
                intersectRDD = oldNewsRDD.intersection(newsRDD)
            except:
                pass # empty rdd
        
        oldNewsRDD = newsRDD
        
        try:
            sendRecord(intersectRDD)
            #TODO save
        except:
            pass # empty rdd
                
        time.sleep(taskdt)
        
    running = False # TODO remove it
    

if __name__ == "__main__":
    run()