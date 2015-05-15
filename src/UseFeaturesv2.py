# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 14:48:06 2015

@author: droz
"""
'''
import os
os.environ['HOME'] = '/tmp'
os.environ['SPARK_WORKER_DIR'] = '/tmp'
'''
from DataManager import News
from DataManager import MarketStatus
from FeaturesManager import FeaturesV2
from random import randint
import datetime
from pyspark import SparkContext
from pyspark.mllib.regression import LabeledPoint
from MessageManager import MessageManager
from DataClassifier import DataClassifier
from DataClassifierV2 import ClassifiersWrapper
from pyspark.mllib.classification import SVMWithSGD, LogisticRegressionWithSGD, LogisticRegressionWithLBFGS
from pyspark.mllib.feature import HashingTF

class DataSetMakerV2(object):
    def __init__(self, n=10000):
        self.n = n
        
    def processKeepNews(self, newsRDD):
        hashingTF = HashingTF(self.n)
        self.newsRDD = newsRDD
        self.featuresRDD = newsRDD.map(lambda x: FeaturesV2(x))

        self.labeledPointsRdd = self.featuresRDD.map(lambda x: (x.news, LabeledPoint(x.giveClasseN(1), hashingTF.transform(x.words + x.bg2 + x.bg3))))
        
        return self.labeledPointsRdd
        
    def process(self, newsRDD):
        hashingTF = HashingTF(self.n)
        self.newsRDD = newsRDD
        self.featuresRDD = newsRDD.map(lambda x: FeaturesV2(x))
        
        #toto = self.featuresRDD.take(1)[0]
        #print(toto.words + toto.bg2 + toto.bg3)

        self.labeledPointsRdd = self.featuresRDD.map(lambda x: LabeledPoint(x.giveClasseN(1), hashingTF.transform(x.words + x.bg2 + x.bg3)))
        
        try:
        
            nbVeryPos = self.featuresRDD.filter(lambda x: x.giveClasseN(1) == 3).count()
            nbPos = self.featuresRDD.filter(lambda x: x.giveClasseN(1) == 2).count()
            nbNeg = self.featuresRDD.filter(lambda x: x.giveClasseN(1) == 1).count()
            nbVeryNeg = self.featuresRDD.filter(lambda x: x.giveClasseN(1) == 0).count()
            nbTot = self.featuresRDD.count()
            
            print("nbTot %d" % nbTot)
            print("\tnbVeryNeg %d" % nbVeryNeg)
            print("\tnbNeg %d" % nbNeg)
            print("\tnbPos %d" % nbPos)
            print("\tnbVeryPos %d" % nbVeryPos)
        except:
            pass # empty rdd
        
        return self.labeledPointsRdd
       

class DataSetMaker(object):
    def __init__(self):
        pass
        
    def process(self, newsRDD):
        self.newsRDD = newsRDD
        self.featuresRDD = newsRDD.map(lambda x: FeaturesV2(x)).distinct()

        allWordsFlat = self.featuresRDD.flatMap(lambda x: list(x.words))
        self.allWordsFlatUnique = allWordsFlat.distinct().sortBy(lambda x: x)
        
        allBg2Flat = self.featuresRDD.flatMap(lambda x: list(x.bg2))
        self.allBg2FlatUnique = allBg2Flat.distinct().sortBy(lambda x: x)
        
        #print(str(self.allWordsFlatUnique.collect()))
        
    def vectorize(self):

        print('debut vectorize')        
        
        self.indexFeatures = self.featuresRDD.zipWithIndex()
        self.indexFeaturesReverse = self.indexFeatures.map(lambda x: (x[1], x[0]))
        self.indexWords = self.allWordsFlatUnique.zipWithIndex()
        self.indexBg2 = self.allBg2FlatUnique.zipWithIndex()
           
        featuresCrossWords = self.indexFeatures.cartesian(self.indexWords)
        featuresCrossBG2 = self.indexFeatures.cartesian(self.indexBg2)
        # ((features, 1), ('toto', 5))
        # x[0][0] = features
        # x[0][1] = features id
        # x[1][0] = word
        # x[1][1] = word id
        # (1, (5, 0))
        vectFlatFeaturesXWords = featuresCrossWords.map(lambda x: (x[0][1], (x[1][1], 1 if x[1][0] in x[0][0].words else 0)))
        vectFlatFeaturesXBG2 = featuresCrossBG2.map(lambda x: (x[0][1], (x[1][1], 1 if x[1][0] in x[0][0].bg2 else 0)))
        
        vectGroupedFeaturesXWords = vectFlatFeaturesXWords.groupByKey()
        vectGroupedFeaturesXBG2 = vectFlatFeaturesXBG2.groupByKey()

        featuresOfWords = vectGroupedFeaturesXWords.mapValues(lambda x: [a[1] for a in sorted(x, key=lambda b: b[0])]).cache()
            
        featuresOfBG2 = vectGroupedFeaturesXBG2.mapValues(lambda x: [a[1] for a in sorted(x, key=lambda b: b[0])]).cache()
        
        self.labelPointsRdd = featuresOfWords.union(featuresOfBG2).reduceByKey(lambda a,b: a+b).join(self.indexFeaturesReverse).mapValues(lambda x: LabeledPoint(x[1].isGood(), x[0])).values()
        
        return self.labelPointsRdd
       
        #print(str(self.indexBg2.collect()))
        

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
    date = datetime.datetime.now()
    m1 = MarketStatus(market_date=date, market_open=10, market_high=10, 
             market_low=10, market_close=10, market_volume=10)
    m2 = MarketStatus(market_date=date, market_open=11, market_high=11, 
         market_low=11, market_close=11, market_volume=11)
    m3 = MarketStatus(market_date=date, market_open=12, market_high=12, 
         market_low=12, market_close=12, market_volume=12)
         
    return News(pubDate=date, symbole='NASDAQ:GOOGL', publication=txt, pubSource='Reuteurs', marketStatus=[m1,m2,m3])

if __name__ == "__main__":
    allNews = [createRandomNews() for x in range(30)]
    sc = SparkContext()
    newsRDD = sc.parallelize(allNews).distinct()
    dataSetMaker = DataSetMakerV2()
    fullDataSet = dataSetMaker.process(newsRDD)
    fullDataSet.cache()
    myClassifier = ClassifiersWrapper()
    myClassifier.addClassifier(classifier=SVMWithSGD, trainParameters={}, weight=0.3)
    myClassifier.addClassifier(classifier=LogisticRegressionWithSGD, trainParameters={}, weight=0.3)
    myClassifier.addClassifier(classifier=LogisticRegressionWithLBFGS, trainParameters={}, weight=0.3)
    dc = DataClassifier(fullDataSet, myClassifier)
    MessageManager.debugMessage("main : start crossvalidation")
    precMin, precMax, prec = dc.crossvalidation(5)
    print('min : %f, max : %f, mean : %f' % (precMin, precMax, prec))
    '''
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
    '''