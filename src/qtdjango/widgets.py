# -*- coding: utf-8 -*-


'''
@author: darvin
'''
from qtmodels import ListModel
from models import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, Qt


class Widget(object):
    def __init__(self):
        pass

        
    def getData(self):
        raise NotImplementedError
    
    def setData(self, data):
        raise NotImplementedError


class LabelWidget(QLabel, Widget):
    def __init__(self):
        Widget.__init__(self)
        QLabel.__init__(self)
        
    def getData(self):
        return self.text()
    
    def setData(self, data):
        if data is not None:
            self.setText(str(data))

class ForeignKeyWidget(QComboBox, Widget):
    def __init__(self, model):
        Widget.__init__(self)
        QComboBox.__init__(self)
        self.model = model


        
    def getData(self):
        return None
    
    def setData(self, data):
        self.qtmodel = ListModel(parent=self, filter=None,\
                                model=self.model)
        self.setModel(self.qtmodel)
        if data is not None:
            pass #FIXME



class SpinBoxWidget(QSpinBox, Widget):
    def __init__(self):
        Widget.__init__(self)
        QSpinBox.__init__(self)
        
    def getData(self):
        return self.value
    
    def setData(self, data):
        if data is not None:
            self.value = data


class ComboBoxWidget(QComboBox, Widget):
    def __init__(self):
        Widget.__init__(self)
        QComboBox.__init__(self)
        
    def getData(self):
        return self.value
    
    def setData(self, data):
        if data is not None:
            self.value = data


class TextEditWidget(QTextEdit, Widget):
    def __init__(self):
        Widget.__init__(self)
        QTextEdit.__init__(self)
        
    def getData(self):
        return self.toPlainText()
    
    def setData(self, data):
        if data is not None:
            self.setPlainText(QtCore.QString(data))


class LineEditWidget(QLineEdit, Widget):
    def __init__(self):
        Widget.__init__(self)
        QLineEdit.__init__(self)
        
    def getData(self):
        return unicode(self.text())
    
    def setData(self, data):
        if data is not None:
            self.setText(QtCore.QString(data))


class IdLabelWidget(QLabel, Widget):
    def __init__(self):
        Widget.__init__(self)
        QLabel.__init__(self)
        
    def getData(self):
        res = self.text().toInt()
        if res[1]:
            return res[0]
        else:
            return None
    
    def setData(self, data):
        if data is not None:
            self.setText(str(data))


