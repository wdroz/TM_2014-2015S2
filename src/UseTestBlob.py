# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 09:23:36 2015

DO NOT USE - DEPRECIATE

@author: droz
"""
import os
from os import listdir
os.environ['HOME'] = '/tmp'
os.environ['SPARK_WORKER_DIR'] = '/tmp'
from textblob import TextBlob
from pyspark import SparkContext
from subprocess import call

def install(x):
    #if(not os.path.isdir("/home/hadoop/nltk_data")):
    #call(["unzip", "*.zip"]) #,"-d", "/home/hadoop/"])
    os.environ['HOME'] = '/tmp'
    import textblob.download_corpora
    textblob.download_corpora.download_all()
    


def showDir(x):
    toto = [ f for f in listdir('.') ]
    myString = 'MY WD : '
    for f in toto:
        myString += '\t' + str(f) + '\n'
    return myString


def createTB(x):
    #os.environ['HOME'] = '/tmp'
    return TextBlob(x)
    
def giveNbWord(x):
    #os.environ['HOME'] = '/tmp'
    return len(x.words)
    
def reduceSum(a,b):
    #os.environ['HOME'] = '/tmp'
    return a+b

if __name__ == "__main__":
    
    sc = SparkContext()
    
        
    for s in sc.parallelize(xrange(100)).map(install).collect():
        pass
    
    print('INSTALL OK')
    
    rdd = sc.parallelize(['hi, how are you?','I am fine, and you ?','I am fine too'])
    
    #nbWord = rdd.map(lambda x: TextBlob(x)).map(lambda w:len(w.words)).reduce(lambda a,b: a+b)
    nbWord = rdd.map(createTB).map(giveNbWord).reduce(reduceSum)
    print('nb words : %d' % nbWord)