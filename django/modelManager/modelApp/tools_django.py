# -*- coding: utf-8 -*-
"""
Created on Fri May 22 13:31:15 2015

@author: droz
"""
from datetime import timedelta
from django.utils import timezone
def matrix_normalize(matrix):
    w = len(matrix)
    h = len(matrix[0])
    for y in range(h):
        mySum = 0
        for x in range(w):
            mySum += matrix[x][y]
        for x in range(w):
            try:
                matrix[x][y] = (matrix[x][y]/float(mySum))*100
            except:
                pass #divide by zero
    
def predictPointToList(predictPoints, hours=48, numberOfX=12):
    #end = datetime.now()
    end = timezone.now() + timedelta(hours=0) #TODO check real hour
    start = end - timedelta(hours=hours)
    nbInLine = []
    for i in range(numberOfX):
        nbInLine.append(0)
    # interpolate and make bins
    dx = hours/float(numberOfX-1)
    for p in predictPoints:
        if(p.newsPubDate <= end and p.newsPubDate >= start):
            for i in range(numberOfX):
                perfect = start + timedelta(hours=dx*i)
                left = perfect - timedelta(hours=dx/2)
                right = perfect + timedelta(hours=dx/2)
                if(p.newsPubDate >= left and p.newsPubDate <= right):
                    nbInLine[i] += 1
                    break
    return nbInLine