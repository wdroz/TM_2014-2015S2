from django.shortcuts import render
from modelApp.models import PredictModel
from modelApp.models import PredictGraph
from django.http import HttpResponse

import pygal
from datetime import datetime
from datetime import timedelta

# Create your views here.
def index(request):
    return render(request, 'index.html', {})
    
def showModels(request):
    myPredictModels = PredictModel.objects.all()
    return render(request, 'showmodels.html', {'models' : myPredictModels})
    
def graph(request, graph_name):
    graph = PredictGraph.objects.get(name=graph_name)
    datey = pygal.DateY(x_label_rotation=20, pretty_print=True)
    pList = []
    for p in graph.predictpoint_set.all():
        myDate = p.newsPubDate
        pList.append((myDate, p.predictScore))
    
    now = datetime.now()
    x_list = [now - timedelta(hours=24), now]
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