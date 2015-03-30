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
    news1 = createRandomNews()
    news2 = createRandomNews()
    news3 = createRandomNews()
    
    allNews = [news1, news2, news3]
    
    for myNews in allNews:
        toto = FeaturesV2(myNews)
        print(str(toto.bg3))