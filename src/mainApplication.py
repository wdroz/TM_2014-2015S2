# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 13:08:00 2015

@author: droz
"""

from StreamingToDjango import StreamingToDjango
import requests
import config
from ast import literal_eval
import time
from multiprocessing import Process
from subprocess import call

def _fctSubProcess(model, graph_name):
    call(['echo', "%s %s" % (model, graph_name)])

def runAsync(model, graph_name):
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
    