from django.shortcuts import render
from modelApp.models import PredictModel
from modelApp.models import PredictGraph
from modelApp.models import PredictPoint
from django.http import HttpResponse
from django.utils import timezone
from ast import literal_eval

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
    hours = 50
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
    
def getTrainingEntry(request, model_name):
    if(model_name):
        try:
            myPredictModel = PredictModel.objects.get(name=model_name)
            entry = myPredictModel.entry_set.all()
            myList = []
            for record in entry:
                subDict = {}
                subDict['symboles'] = []
                subDict['keywords'] = []
                for symbole in record.symbole_set.all():
                    subDict['symboles'].append(symbole.symbole)
                for keyword in record.keyword_set.all():
                    subDict['keywords'].append(keyword.keyword)
                myList.append(subDict)
            return HttpResponse(str(myList))
        except Exception as e:
            return HttpResponse(str(e)) # TODO improve error
    return HttpResponse('') # TODO improve error

def getStreamingSymbole(request, graph_name):
    if(graph_name):
        try:
            myGraphModel = PredictGraph.objects.get(name=graph_name)
            symbole = myGraphModel.symbole
            return HttpResponse(str(symbole))
        except Exception as e:
            return HttpResponse(str(e)) # TODO improve error
    return HttpResponse('') # TODO improve error
    
def prediction(request, model_name):
    if(model_name == None):
        return showModels(request)
    try:
        myPredictModel = PredictModel.objects.get(name=model_name)
        return render(request, 'prediction.html', {'model' : myPredictModel})
    except:
        return showModels(request) # TODO better error
    
def addPoint(request, graph_name):
    if(graph_name == None):
        return HttpResponse('')
    try:
        myPredictGraph = PredictGraph.objects.get(name=graph_name)
        point = request.POST # no security
        newPoint = PredictPoint(newsPubDate=point['newsPubDate'], newsSource=point['newsSource'], newsText=['newsText'], predictScore=point['predictScore'], predictGraph=myPredictGraph)
        newPoint.save()
        return HttpResponse('OK')
    except Exception as e:
            return HttpResponse(str(e)) # TODO improve error