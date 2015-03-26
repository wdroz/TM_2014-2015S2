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
Builder.load_file('ui_search.kv')

class DeleteButton(ButtonBehavior, Image):
    pass

class SearchField(BoxLayout):
    def __init__(self, **kwargs):
        super(SearchField, self).__init__(**kwargs)
        self.txtSymbol.text = kwargs['symbol']
        self.txtKeywords.text = kwargs['keywords']

    def delete_me(self):
        self.parent.remove_widget(self)
        print('delete me')

class MySearchUI(BoxLayout):
    def __init__(self, **kwargs):
        super(MySearchUI, self).__init__(**kwargs)
        
    def add_search(self):
        print('salut')
        sf = SearchField(symbol=self.txtSymbol.text, keywords=self.txtKeywords.text)
        self.lyListOfSearch.add_widget(sf)

class TestApp(App):
    def build(self):
        return MySearchUI()
        
TestApp().run()
