# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 12:34:44 2015

@author: droz
"""


from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from ast import literal_eval
Builder.load_file('ui_search.kv')

class DeleteButton(ButtonBehavior, Image):
    pass

class SearchField(BoxLayout):
    def __init__(self, **kwargs):
        super(SearchField, self).__init__(**kwargs)
        self.txtSymbol.text = kwargs['symbol']
        self.txtKeywords.text = kwargs['keywords']
        self.searchUI = kwargs['searchUI']

    def delete_me(self):
        self.searchUI.delete_item(self.txtSymbol.text)
        self.parent.remove_widget(self)
        print('delete me')

class MySearchUI(BoxLayout):
    def __init__(self, **kwargs):
        super(MySearchUI, self).__init__(**kwargs)
        self.filepath='symbols.conf'
        self.dicoList = []
        self.loadFromFile(self.filepath)
        
    def start(self):
        self.saveToFile(self.filepath)
        self.progress.value=100
        
    def loadFromFile(self,filepath):
        with open(self.filepath, 'r') as f:
            lines = f.read().split('\n')
            for line in lines:
                self.loadLine(line)
            
    def loadLine(self, line):
        try:
            dico = literal_eval(line)
            self._add_search(dico['symbol'], ';'.join(dico['keywords']))
        except:
            pass # empty line
    
    def saveToFile(self, filepath):
        with open(filepath, 'w') as f:
            for dico in self.dicoList:
                f.write(str(dico)+'\n')
        
    def add_search(self):
        self._add_search(self.txtSymbol.text, self.txtKeywords.text)
        
    def _add_search(self, symbol, keywords):
        try:
            dico = {}
            dico['symbol'] = symbol
            dico['keywords'] = keywords.split(';')
            self.dicoList.append(dico)
            sf = SearchField(symbol=symbol, keywords=keywords, searchUI=self)
            self.lyListOfSearch.add_widget(sf)
        except:
            pass # bad format
    def delete_item(self, symbol):
        for i in range(len(self.dicoList)):
            if(self.dicoList[i]['symbol'] == symbol):
                self.dicoList.remove(self.dicoList[i])
                break;

class TestApp(App):
    def build(self):
        return MySearchUI()
        
TestApp().run()
