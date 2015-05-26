from django.shortcuts import render
from modelApp.models import PredictModel
from modelApp.models import PredictGraph
from django.http import HttpResponse
from django.utils import timezone

import pygal
from datetime import timedelta
from tools_django import matrix_normalize
from tools_django import predictPointToList
# Create your views here.
def index(request):
    return render(request, 'index.html', {})
    
def showModels(request):
    myPredictModels = PredictModel.objects.all()
    return render(request, 'showmodels.html', {'models' : myPredictModels})
        
def graph(request, graph_name):
    hours = 48
    numberOfX = 4
    
    graph = PredictGraph.objects.get(name=graph_name)
    
    #end = datetime.now()
    end = timezone.now()
    start = end - timedelta(hours=hours)

    labels = []
    dx = hours/float(numberOfX-1)
    for i in range(numberOfX):
        labels.append(str(start + timedelta(hours=dx*i)))
    stackedline_chart = pygal.StackedLine(fill=True, x_label_rotation=30)
    stackedline_chart.title = 'market prediction (in %) [' + str(graph_name) + ']'
    stackedline_chart.x_labels = labels
    veryBad = predictPointToList(graph.predictpoint_set.filter(predictScore=0.0), hours=hours, numberOfX=numberOfX)
    bad = predictPointToList(graph.predictpoint_set.filter(predictScore=1.0), hours=hours, numberOfX=numberOfX)
    good = predictPointToList(graph.predictpoint_set.filter(predictScore=2.0), hours=hours, numberOfX=numberOfX)
    veryGood = predictPointToList(graph.predictpoint_set.filter(predictScore=3.0), hours=hours, numberOfX=numberOfX)
    matrix_normalize([veryBad, bad, good, veryGood])

    stackedline_chart.add('Very bad', veryBad)
    stackedline_chart.add('Bad', bad)
    stackedline_chart.add('Good', good)
    stackedline_chart.add('Very good', veryGood)
    return HttpResponse(stackedline_chart.render()) 
    #stackedline_chart.render()
    
def prediction(request, model_name):
    if(model_name == None):
        return showModels(request)
    try:
        myPredictModel = PredictModel.objects.get(name=model_name)
    except:
        return showModels(request) # TODO better error
    return render(request, 'prediction.html', {'model' : myPredictModel})