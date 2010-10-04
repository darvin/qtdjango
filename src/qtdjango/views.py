# -*- coding: utf-8 -*-


'''
@author: darvin
'''

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
        


class BaseView(object):
    '''
    classdocs
    '''
    fieldwidgets_dict = {TextField:TextEditWidget,
                         IdField:IdLabelWidget,
                       CharField:LineEditWidget,
                       IntegerField:SpinBoxWidget,
                       ForeignKey:ComboBoxWidget
                       }
    fields = ()
    widgets = {}
    model = None

    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        if self.fields == ():
            self.fields = [x for x in self.model.get_fields()]
            
        
        
        
        
        
class DetailView(QDialog, BaseView):
    
    def __init__(self, parent=None, **kwargs):
        QDialog.__init__(self, parent, **kwargs)
        BaseView.__init__(self, **kwargs)
        
        
        self.formlayout = QFormLayout()
        
        self._widgets={}
        for field in self.fields:
            x = self.model.fields[field]
            try:
                self._widgets[field] = self.widgets[field]
            except KeyError:
                self._widgets[field] = self.fieldwidgets_dict[x.__class__]()
            self.formlayout.addRow(x.get_label(), self._widgets[field])
            
        self.get_data_from_model()   
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                      | QDialogButtonBox.Cancel)
        
        Qt.QObject.connect(buttonBox, Qt.SIGNAL("accepted()"), self, Qt.SLOT("accept()"));
        Qt.QObject.connect(buttonBox, Qt.SIGNAL("rejected()"), self, Qt.SLOT("reject()"));
        self.formlayout.addRow(buttonBox)
        self.setLayout(self.formlayout)
    
    def get_data_from_model(self):
        for field in self.fields:
            self._widgets[field].setData(getattr(self.model,field))
        
        
    def set_data_to_model(self):
        changed = False
        for field in self.fields:
            x = self.model.fields[field]
            newvalue = x.dump(self._widgets[field].getData())
            if newvalue!=getattr(self.model, field):
                setattr(self.model, field, newvalue)
                changed = True
        if changed:
            self.model.save()

    def accept(self):
        QDialog.accept(self)
        self.set_data_to_model()




class TableModel(QtCore.QAbstractTableModel):

        
    def __init__(self, model, filter, fields, parent=None,  *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        
        self.model = model
        self.filter = filter    
        self.fields = fields
      
    def filtered_model(self):
        if self.filter is None:
            return self.model.all()
        else:
            return self.model.filter(**self.filter)
    
    def columnCount(self, parent):
        return len(self.fields)

    def rowCount(self, parent):
        return len(self.filtered_model())

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            return QtCore.QVariant()
        elif orientation == QtCore.Qt.Horizontal:
            return QtCore.QString.fromUtf8(self.model.get_fields()[self.fields[section]].get_label())
        

    def data(self, index, role):
        data = self.filtered_model()
        
        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()


        field_raw_data = getattr(data[index.row()],self.fields[index.column()])
        result = self.model.get_fields()[self.fields[index.column()]].dump(field_raw_data)
        return QtCore.QVariant(result)



class ListView(BaseView):
    def __init__(self, filter=None):
        BaseView.__init__(self)
        self.filter = filter
    
    def set_filter(self, filter):
        self.filter = filter
    

class TableView(QTableView, ListView):
    def __init__(self, filter=None):
        QTableView.__init__(self)
        ListView.__init__(self, filter)
        self.tablemodel = TableModel(self.model, self.filter, self.fields)
        self.setModel(self.tablemodel)
        
    def set_filter(self, filter):
        ListView.set_filter(self, filter)
        self.tablemodel.set_filter(self.filter)



    
