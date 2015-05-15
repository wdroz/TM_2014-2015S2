# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 10:05:01 2015

@author: droz
"""

from DataManager import News, NewsPrediction

from flask import Flask, request
from flask_restful import Resource, Api
import json

app = Flask(__name__)
api = Api(app)

predictions = {}

classesMap = {'3' : 'very good', '2' : 'good', '1' : 'bad', '0' : 'very bad'}

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
    app.run(host='0.0.0.0', debug=True)