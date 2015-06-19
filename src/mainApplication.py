# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 13:08:00 2015

@author: droz

Entry point

"""

#from StreamingToDjango import StreamingToDjango
import requests
import config
from ast import literal_eval
import time
from multiprocessing import Process
from subprocess import call
from os import environ

def _fctSubProcess(model, graph_name):
    '''
    launch spark job for model and graph_name
    '''
    env = environ.copy()
    #/spark-1.3.1-bin-hadoop2.4/bin/spark-submit --deploy-mode client --master yarn-client --py-files \"$zipString\" --archives \"nltk_data.zip\" $main")
    cmd = '%s/bin/spark-submit' % env['SPARK_HOME']
    args = []
    args.append(cmd)
    args.append('--deploy-mode')
    args.append('client')
    args.append('--master')
    args.append('yarn-client')
    args.append('--py-files')
    args.append('PySrc3.zip,PySrc2.zip,PySrc1.zip')
    args.append('StreamingToDjango.py')
    args.append(str(model))
    args.append(str(graph_name))
    #arg = '--deploy-mode client --master yarn-client --py-files "PySrc3.zip,PySrc2.zip,PySrc1.zip" StreamingToDjango.py ' + '"%s" "%s"' % (model, graph_name)
    print(args)
    call(args)

def runAsync(model, graph_name):
    '''
    run function async.
    '''
    Process(target=_fctSubProcess, args=(model, graph_name)).start()

if __name__ == "__main__":
    combi = []
    while(True):
        url = config.DJANGO_CONF['url'] + '/' + config.DJANGO_CONF['combi']
        r = requests.get(url)
        #print(r.text)
        currentCombi = literal_eval(r.text)
        for c in currentCombi:
            if c not in combi:
                runAsync(c[0], c[1])
                combi.append(c)
        time.sleep(10)
    