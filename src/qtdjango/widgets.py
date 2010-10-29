# -*- coding: utf-8 -*-


'''
@author: darvin
'''
from qtmodels import ListModel
from models import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, Qt
from PyQt4.QtCore import QDateTime


class Widget(object):
    def __init__(self, field):
        self.field = field

        
    def getData(self):
        raise NotImplementedError
    
    def setData(self, data):
        raise NotImplementedError


class LabelWidget(QLabel, Widget):
    def __init__(self, field):
        Widget.__init__(self, field)
        QLabel.__init__(self)
        
    def getData(self):
        return unicode(self.text())
    
    def setData(self, data):
        if data is not None:
            self.setText(str(data))

class ForeignKeyWidget(QComboBox, Widget):
    def __init__(self, field):
        Widget.__init__(self, field)
        QComboBox.__init__(self)
        self.model = self.field.model


    def set_filter(self, filter):
        self.qtmodel.set_filter(filter)

    def getData(self):
        try:
            return self.qtmodel.get_model_instance_by_int_index(\
                self.currentIndex())
        except IndexError:
            return None

    def setData(self, data):
        self.qtmodel = ListModel(parent=self, filter=None,\
                                model=self.model, blank_variant=self.field.blank)
        self.setModel(self.qtmodel)
        if data is not None:
            self.setCurrentIndex(self.qtmodel.get_index_of_model(data))



class SpinBoxWidget(QSpinBox, Widget):
    def __init__(self, field):
        Widget.__init__(self, field)
        QLabel.__init__(self)
        self.setMinimum(0)
        self.setMaximum(999999)

    def getData(self):
        return self.value()
    
    def setData(self, data):
        if data is not None:
            self.setValue = data

class DateTimeEditWidget(QDateTimeEdit, Widget):
    def __init__(self, field):
        Widget.__init__(self, field)
        QDateTimeEdit.__init__(self)

    def getData(self):
        return self.dateTime().toPyDateTime()

    def setData(self, data):
        if data is not None:
            self.setDateTime(data)
        else:
            self.setDateTime(QDateTime.currentDateTime())

class CheckBoxWidget(QCheckBox, Widget):
    def __init__(self, field):
       Widget.__init__(self, field)
       QCheckBox.__init__(self)

    def getData(self):
        return self.isChecked()
    def setData(self, data):
        if data is None:
            data = False
        self.stateChanged.emit(data)

class ComboBoxWidget(QComboBox, Widget):
    def __init__(self, field):
        Widget.__init__(self, field)
        QComboBox.__init__(self)
        
    def getData(self):
        return self.value
    
    def setData(self, data):
        if data is not None:
            self.value = data


class TextEditWidget(QTextEdit, Widget):
    def __init__(self, field):
        Widget.__init__(self, field)
        QTextEdit.__init__(self)

    def getData(self):
        return unicode(self.toPlainText())
    
    def setData(self, data):
        if data is not None:
            self.setPlainText(QtCore.QString(data))


class LineEditWidget(QLineEdit, Widget):
    def __init__(self, field):
        Widget.__init__(self, field)
        QLineEdit.__init__(self)

    def getData(self):
        return unicode(self.text())
    
    def setData(self, data):
        if data is not None:
            self.setText(QtCore.QString(data))


class IdLabelWidget(QLabel, Widget):
    def __init__(self, field):
        Widget.__init__(self, field)
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


