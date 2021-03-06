# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 13:27:05 2015

@author: droz
"""

import HTMLParser
import re
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
from DataManager import News, NewsPrediction
import pickle
import requests
from ast import literal_eval
import datetime        
from collections import defaultdict
import json
import time

def tryOrSet(listOfItems, index, defaultValue):
    '''
    try to access to listOfItems at index. if fail return defaultValue
    '''
    try:
        return listOfItems[index]
    except:
        return defaultValue

class FeedNewsFromGoogleFinance(object):
    '''
    retrieve news from google finance
    '''
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
            for cpt in range(len(quotes)):
                try:
                    #Feb 26, 2015
                    date = datetime.datetime.strptime(dates[cpt], "%b %d, %Y")
                    recentNews.append(News(pubDate=date, symbole=symbole, publication=quotes[cpt], pubSource=sources[cpt]))
                    print('sources : %s' % sources)
                except:
                    pubSource = tryOrSet(sources, cpt, 'inconnu')
                    pubDate = datetime.datetime.now() # TODO minus time delta
                    publication = tryOrSet(quotes, cpt, 'pas de text')
                    recentNews.append(News(pubDate=pubDate, symbole=symbole, publication=publication, pubSource=pubSource, resetTime=False))
                    
            params['start'] += self.num
        print('nb news found: %d' % len(recentNews))    
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
    
    feed = FeedNewsFromGoogleFinance()
    
    def sendRecord(rdd):
        print('new try...')
        if(not rdd.isEmpty()):
            newsRDD = dataSetMaker.processKeepNews(rdd)
            res = newsRDD.map(lambda x: (x[0], myClassifierOnevsOne.predict(x[1].features)))
            print('for each result...')
            for result in res.collect():
                symbole = result[0].symbole
                r = requests.put('http://wtun.mooo.com:5000', data={'jdata' : NewsPrediction(result[0], str(result[1])).json(),  'symbole' : symbole, 'label' : str(result[1])})
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
    cpt = 0
    while(running):
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        newsRDD = symbolesRDD.flatMap(lambda x: feed.lookingAt(x[0], yesterday, tomorrow, x[1]))
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
            intersectRDD.saveAsPickleFile(dataDirectory + '/' + datetime.datetime.now().strftime('%Y-%m-%d--') + str(cpt))
            cpt += 1
        except:
            pass # empty rdd
                   
        time.sleep(taskdt)
        
    running = False # TODO remove it
    

if __name__ == "__main__":
    run()