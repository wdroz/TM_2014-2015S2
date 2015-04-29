# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 10:05:01 2015

@author: droz
"""
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

predictions = {}

classesMap = {'0' : 'very good', '1' : 'good', '2' : 'bad', '3' : 'very bad'}

class PredictionsSimple(Resource):
    
    def put(self):
        symbole = request.form['symbole']
        predictions[symbole] = request.form['label']
        res = {symbole: predictions[symbole]}
        print('receive new predictions for %s with classes %s -> %s' %(symbole, predictions[symbole], classesMap[predictions[symbole]]))
        return res 

api.add_resource(PredictionsSimple, '/')

if __name__ == '__main__':
    app.run(debug=True)