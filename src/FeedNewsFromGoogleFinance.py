# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 13:27:05 2015

@author: droz
"""

import HTMLParser
import re
import requests
import datetime

from DataManager import News

class FeedNewsfromGoogleFinance(object):
    def __init__(self, hdfsPath, listSymboles=[], intervalSecondes=30):
        self.hdfsPath = hdfsPath
        self.listSymboles = listSymboles
        self.intervalSecondes = intervalSecondes
        self.url = 'https://www.google.com/finance/company_news'
        self.expNews = '<div style="width:100%;">([^/]+)</div>'
        self.expDate = '<span class=date>([^/]+)</span>'
        self.expPubSource = '<span class=src>([^/]+)</span>'
        self.num = 10
        self.h = HTMLParser.HTMLParser()
        self.oldNews = []
        self.recentNews = []
        
    def lookingAt(self, symbole, startDate, endDate, keywords):
        hasMoreQuote=True
        params = {'q' : symbole, 'startdate' : str(startDate.strftime('%Y-%m-%d')), 'enddate' : str(endDate.strftime('%Y-%m-%d')), 'start' : 0, 'num' : self.num}
        while(hasMoreQuote):
            r = requests.get(self.url, params=params)
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
                    self.oldNews.append(News(pubDate=date, symbole=symbole, publication=quotes[cpt], pubSource=sources[cpt]))
                except:
                    self.RecentNews.append(News(pubDate=datetime.datetime.now(), symbole=symbole, publication=quotes[cpt], pubSource=sources[cpt]))
            params['start'] += self.num

def run():
    pass

if __name__ == "__main__":
    pass