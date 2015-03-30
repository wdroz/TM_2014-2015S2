# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 08:11:44 2015

@author: droz
"""
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from TextToVect import VectorManager
from ast import literal_eval
from textblob import Word, TextBlob
from DataClassifier import DataClassifier

def lemmatize(textblob):
    '''
    permet d'avoir une list de mot lemmanizé
    '''
    words = []
    for word in textblob.words:
        myWord = Word(word.lemmatize('v').encode('utf-8'))
        myWord = Word(myWord.lemma)
        myWord = Word(myWord.singularize().upper().encode('utf-8'))
        words.append(myWord)
    return words
    
def printPrediction(rdd):
    for k,v in rdd.collect():
        print('%s from %s is classified as %s' % (k['text'], k['source'], v))

if __name__ == "__main__":

    vm = VectorManager(None)
    vm.load()    
    dc = DataClassifier(None, None)
    dc.loadModel()
    
    sc = SparkContext(appName="PythonStreaming")
    ssc = StreamingContext(sc, 30)
    
    #streamPath = 'hdfs://157.26.83.52/user/wdroz/stream'    
    streamPath = '/tmp/stream'    
    '''
    Data each line is {text : 'bla bla bla', source : 'bla bla', date : '2015-30-03 08:53:00'}
    '''
    lines = ssc.textFileStream(streamPath)
    
    dico = lines.map(lambda x: literal_eval(x))
    
    lema = dico.map(lambda x: (x, lemmatize(TextBlob(x['text']))))
    
    vect = lema.mapValues(lambda x: vm.processList(x))
    
    pred = vect.mapValues(lambda x: dc.predict(x))
    
    pred.foreachRDD(printPrediction)
        
    
    ssc.start()
    ssc.awaitTermination()