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

class PredictionsSimple(Resource):
    
    def put(self):
        symbole = request.form['symbole']
        predictions[symbole] = request.form['label']
        return {symbole: predictions[symbole]}

api.add_resource(PredictionsSimple, '/')

if __name__ == '__main__':
    app.run(debug=True)