# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 10:05:01 2015

@author: droz
"""

from DataManager import News

from flask import Flask, request
from flask_restful import Resource, Api
import json

app = Flask(__name__)
api = Api(app)

predictions = {}

classesMap = {'0' : 'very good', '1' : 'good', '2' : 'bad', '3' : 'very bad'}

class NewsPrediction(object):
    def __init__(self, news=None, prediction=0):
        try:
            self.prediction = prediction
            self.publication = news.publication
            self.pubDate = str(news.pubDate)
            self.pubSource = news.pubSource 
            self.symbole = news.symbole
        except:
            pass # news is None
        
    def json(self):
        return json.dumps(self.__dict__)
        
    def __str__(self):
        myString = '---\n'
        myString += '%s\t%s\t%s\tfrom %s\n' % (self.symbole, self.pubDate, self.publication, self.pubSource)
        myString += '\tpredValue is %s\n' % self.prediction
        myString += '---'
        return myString

class PredictionsSimple(Resource):
    
    def put(self):
        symbole = request.form['symbole']
        predictions[symbole] = request.form['label']
        res = {symbole: predictions[symbole]}
        news = NewsPrediction()
        news.__dict__ = json.loads(request.form['jdata'].encode('utf-8'))
        print('receive new predictions for %s with classes %s -> %s' %(symbole, predictions[symbole], classesMap[predictions[symbole]]))
        try:        
            print(str(news))
        except:
            pass # encoding issues
        return res 

api.add_resource(PredictionsSimple, '/')

if __name__ == '__main__':
    app.run(debug=True)