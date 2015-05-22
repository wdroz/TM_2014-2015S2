from django.shortcuts import render
from modelApp.models import PredictModel
from modelApp.models import PredictGraph
from django.http import HttpResponse
from django.utils import timezone

import pygal
from datetime import datetime
from datetime import timedelta

# Create your views here.
def index(request):
    return render(request, 'index.html', {})
    
def showModels(request):
    myPredictModels = PredictModel.objects.all()
    return render(request, 'showmodels.html', {'models' : myPredictModels})
    
def predictPointToList(predictPoints, hours=48, numberOfX=12):
    #end = datetime.now()
    end = timezone.now()    
    start = end - timedelta(hours=hours)
    nbInLine = []
    for i in range(numberOfX):
        nbInLine.append(0)
    # interpolate and make bins
    dx = hours/numberOfX
    for p in predictPoints:
        if(p.newsPubDate <= end and p.newsPubDate >= start):
            for i in range(numberOfX):
                left = start + timedelta(hours=dx*i)
                right = left + timedelta(hours=dx)
                if(p.newsPubDate >= left and p.newsPubDate <= right):
                    nbInLine[i] += 1
                    break
    return nbInLine
    
    
def graph_stacked(request, graph_name):
    hours = 48
    numberOfX = 4
    
    graph = PredictGraph.objects.get(name=graph_name)
    
    #end = datetime.now()
    end = timezone.now()    
    start = end - timedelta(hours=hours)

    labels = []
    dx = hours/numberOfX
    for i in range(numberOfX):
        labels.append(str(start + timedelta(hours=dx*i)))
    stackedline_chart = pygal.StackedLine(fill=True, x_label_rotation=30)
    stackedline_chart.title = 'market prediction (in %)'
    stackedline_chart.x_labels = labels
    veryBad = predictPointToList(graph.predictpoint_set.filter(predictScore=0.0), hours=hours, numberOfX=numberOfX)
    bad = predictPointToList(graph.predictpoint_set.filter(predictScore=1.0), hours=hours, numberOfX=numberOfX)
    good = predictPointToList(graph.predictpoint_set.filter(predictScore=2.0), hours=hours, numberOfX=numberOfX)
    veryGood = predictPointToList(graph.predictpoint_set.filter(predictScore=3.0), hours=hours, numberOfX=numberOfX)
    
    stackedline_chart.add('Very bad', veryBad)
    stackedline_chart.add('Bad',  bad)
    stackedline_chart.add('Good',      good)
    stackedline_chart.add('Very good',  veryGood)
    return HttpResponse(stackedline_chart.render()) 
    #stackedline_chart.render()
    
def graph(request, graph_name):
    return graph_stacked(request, graph_name)
    graph = PredictGraph.objects.get(name=graph_name)
    datey = pygal.DateY(x_label_rotation=20, pretty_print=True)
    pList = []
    for p in graph.predictpoint_set.all():
        myDate = p.newsPubDate
        pList.append((myDate, p.predictScore))
    
    now = datetime.now()
    x_list = [now - timedelta(hours=48), now]
    #for i in range(len(pList)):
    #    x_list.append(now + timedelta(hours=-1*i))
    
    datey.add(str(graph_name), pList)
    datey.x_labels = x_list
    #datey.x_label_format = "%Y-%m-%d"
    #datey.x_label_format = "%Y-%m-%d"
    #datey.render_to_png('lol.png')
    return HttpResponse(datey.render()) # image/svg+xml
    
def prediction(request, model_name):
    if(model_name == None):
        return showModels(request)
    try:
        myPredictModel = PredictModel.objects.get(name=model_name)
    except:
        return showModels(request) # TODO better error
    return render(request, 'prediction.html', {'model' : myPredictModel})