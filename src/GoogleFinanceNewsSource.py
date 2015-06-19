# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 09:45:24 2015

@author: droz
"""

from DataManager import NewsSource, News
from MessageManager import MessageManager

import HTMLParser
import re
import requests
import datetime

class GoogleFinanceNewsSource(NewsSource):
    '''
    Classe specialisé pour chercher les informations sur Google Finance
    '''
    def __init__(self):
        NewsSource.__init__(self)
        self.url = 'https://www.google.com/finance/company_news'
        self.expNews = '<div style="width:100%;">([^/]+)</div>'
        self.expDate = '<span class=date>([^/]+)</span>'
        self.expPubSource = '<span class=src>([^/]+)</span>'
        self.num = 10
        self.h = HTMLParser.HTMLParser()
        
    def lookingAt(self, symbole, startDate, endDate, keywords):
        '''
        méthode pour rechercher des news
             -symbole ce qu'on cherche depuis startDate jusqu'à endDate
             avec les keywords dans le contenu
        '''
        hasMoreQuote=True
        params = {'q' : symbole, 'startdate' : str(startDate.strftime('%Y-%m-%d')), 'enddate' : str(endDate.strftime('%Y-%m-%d')), 'start' : 0, 'num' : self.num}
        while(hasMoreQuote):
            r = requests.get(self.url, params=params)
            MessageManager.debugMessage("GoogleFinanceNewsSource : request")
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
                    self.news.append(News(pubDate=date, symbole=symbole, publication=quotes[cpt], pubSource=sources[cpt]))
                except:
                    MessageManager.debugMessage("new recent, ... set for today")
                    self.news.append(News(pubDate=datetime.datetime.now(), symbole=symbole, publication=quotes[cpt], pubSource=sources[cpt]))
            params['start'] += self.num