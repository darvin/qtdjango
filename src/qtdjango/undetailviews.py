# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4 import QtCore, Qt
from baseview import BaseView
from qtmodels import *
from models import Model

class UndetailView(BaseView):
    def __init__(self, filter=None):
        BaseView.__init__(self)
        self.filter = filter

    def set_filter(self, filter):
        self.filter = filter


class UndetailWithButtonsView(QFrame):
    viewclass = None
    buttons = {"delete": (True, u"Удалить"),
               "edit":(True,u"Редактировать"),
               "new":(True,u"Добавить"),
              }
    def __init__(self, *args, **kwargs):
        """docstring for __init__"""
        QFrame.__init__(self)
        self.view = self.viewclass(*args, **kwargs)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.view)
        self.buttonlayout = QHBoxLayout()
        self.layout.addLayout(self.buttonlayout)
        self._buttons = {}
        for button, (buttonexist, buttonname) in self.buttons.items():
            if buttonexist:
                b = QPushButton(buttonname)
                self._buttons[button] = b
                self.buttonlayout.addWidget(b)
                #b.clicked.connect(\
                                  #lambda x:\
                                  #getattr(self.view,"model_"+button)()\
                #                 )
        self._buttons["edit"].clicked.connect(lambda x: self.view.model_edit())
        self._buttons["delete"].clicked.connect(lambda x: self.view.model_delete())
        self._buttons["new"].clicked.connect(lambda x: self.view.model_new())




class AbstactQtModelUndetailView(UndetailView, QAbstractItemView):
    def __init__(self, filter=None):
        QAbstractItemView.__init__(self)
        UndetailView.__init__(self, filter)
        self.qtmodel = self._qt_model_class(self.model, self.filter, self.fields)
        self.setModel(self.qtmodel)
    def set_filter(self, filter):
        UndetailView.set_filter(self, filter)
        self.qtmodel.set_filter(self.filter)

    def create_detail_view(self, model_to_edit=None, filter=None):

        #t = type(self.model.__name__.upper() + "DetailView",\
                 #(DetailView,), {"model":model_to_edit})
        return self.detail_view(parent=self, model_instance=model_to_edit,\
                                filter=filter)

    @QtCore.pyqtSlot()
    def currentChanged (self, mi1, mi2):
        self.modelSelectionChanged.emit( self.qtmodel.get_qtdjango_model_by_index(mi1))

    def model_edit (self):
        dv = self.create_detail_view(\
                    self.qtmodel.get_qtdjango_model_by_index(self.currentIndex()))
        dv.show()

    def model_delete (self):
        print "hi"

    def model_new (self):
        dv = self.create_detail_view(filter=self.filter)
        dv.show()

    def refresh(self):
        self.qtmodel.reset()

class ListView(QListView, AbstactQtModelUndetailView):
    _qt_model_class = ListModel
    modelSelectionChanged = QtCore.pyqtSignal([Model]) ##dont work when in
                                                        #father class
    def __init__(self, filter=None):
        QListView.__init__(self)
        AbstactQtModelUndetailView.__init__(self, filter)




class TableView(QTableView, AbstactQtModelUndetailView):
    _qt_model_class = TableModel
    modelSelectionChanged = QtCore.pyqtSignal([Model]) ##dont work when in
                                                        #father class
    def __init__(self, filter=None):
        QTableView.__init__(self)
        AbstactQtModelUndetailView.__init__(self, filter)




class TreeView(QTreeView, AbstactQtModelUndetailView):
    _qt_model_class = TableModel
    modelSelectionChanged = QtCore.pyqtSignal([Model]) ##dont work when in
                                                        #father class
    def __init__(self, filter=None):
        QTreeView.__init__(self)
        AbstactQtModelUndetailView.__init__(self, filter)
