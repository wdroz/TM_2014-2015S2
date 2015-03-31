# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 14:48:06 2015

@author: droz
"""
from DataManager import News
from DataManager import MarketStatus
from FeaturesManager import FeaturesV2
from random import randint
import time
from pyspark import SparkContext

def createRandomNews():
    pList = ['I am the one who knocks',
             'Do you like cheese?',
             'It is so cool to be a programmer',
             'The red mountains are fabulous',
             'Nobody expect to see mac user here',
             'Unfortunally, they use Apple products',
             'Internet Explorer was deleted by Microsoft last night']
             
    indice = randint(0,len(pList)-1)
    txt = pList[indice]
    date = time.strftime('%Y-%m-%d')
    m1 = MarketStatus(market_date=date, market_open=10, market_high=10, 
             market_low=10, market_close=10, market_volume=10)
    m2 = MarketStatus(market_date=date, market_open=11, market_high=11, 
         market_low=11, market_close=11, market_volume=11)
    m3 = MarketStatus(market_date=date, market_open=12, market_high=12, 
         market_low=12, market_close=12, market_volume=12)
         
    return News(pubDate=date, symbole='NASDAQ:GOOGL', publication=txt, pubSource='Reuteurs', marketStatus=[m1,m2,m3])

if __name__ == "__main__":
    allNews = [createRandomNews() for x in range(10000)]
    sc = SparkContext()
    newsRDD = sc.parallelize(allNews)
    featuresRDD = newsRDD.map(lambda x: FeaturesV2(x))
    allBg2 = featuresRDD.map(lambda x: list(x.bg2)).reduce(lambda a,b : a+b)
    allBg3 = featuresRDD.map(lambda x: list(x.bg3)).reduce(lambda a,b : a+b)
    setAllBg2 = set(allBg2)
    setAllBg3 = set(allBg3)
    print('size of setAllBg2 : %d' % len(setAllBg2))
    print('size of setAllBg3 : %d' % len(setAllBg3))
    
    allBg2Flat = featuresRDD.flatMap(lambda x: list(x.bg2))
    allBg2FlatUnique = allBg2Flat.intersection(allBg2Flat).collect()
    print('size of allBg2FlatUnique %d' % len(allBg2FlatUnique))    