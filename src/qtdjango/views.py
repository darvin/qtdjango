
# -*- coding: utf-8 -*-


'''
@author: darvin
'''
from PyQt4.QtGui import *
from PyQt4 import QtCore, Qt


from widgets import *
from qtmodels import *

class BaseView(object):
    '''
    classdocs
    '''
    fields = ()
    widgets = {}
    model = None

    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        self.model.add_notify(self)
        if self.fields == ():
            self.fields = [x for x in self.model.get_fields()]

    def refresh(self):
        """docstring for dataChanged"""
        pass


class DetailView(QDialog, BaseView):
    fieldwidgets_dict = {TextField:TextEditWidget,
                         IdField:IdLabelWidget,
                       CharField:LineEditWidget,
                       IntegerField:SpinBoxWidget,
                       ForeignKey:ForeignKeyWidget
                       }

    def __init__(self, parent=None, model_instance=None, filter=None,**kwargs):
        QDialog.__init__(self, parent, **kwargs)
        BaseView.__init__(self, **kwargs)
        if model_instance is None:
            self.model_instance = self.model.new()
        else:
            self.model_instance = model_instance
        self.formlayout = QFormLayout()
        self._widgets={}
        for field in self.fields:
            x = getattr(self.model,field)
            try:
                self._widgets[field] = self.widgets[field]
            except KeyError:
                try:
                    if self.fieldwidgets_dict[x.__class__] is ForeignKeyWidget:
                        self._widgets[field] = \
                            self.fieldwidgets_dict[x.__class__](model=x.model)
                    else:
                        self._widgets[field] = \
                            self.fieldwidgets_dict[x.__class__]()

                except KeyError:
                    self._widgets[field] = LabelWidget() ##FIXME!
            self.formlayout.addRow(QtCore.QString.fromUtf8(x.get_label()), self._widgets[field])
        self.get_data_from_model()
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                      | QDialogButtonBox.Cancel)
        Qt.QObject.connect(buttonBox, Qt.SIGNAL("accepted()"), self, Qt.SLOT("accept()"));
        Qt.QObject.connect(buttonBox, Qt.SIGNAL("rejected()"), self, Qt.SLOT("reject()"));
        self.formlayout.addRow(buttonBox)
        self.setLayout(self.formlayout)
        self.set_filter(filter)

    def get_data_from_model(self):
        print self.model_instance.__dict__
        for field in self.fields:
            self._widgets[field].setData(getattr(self.model_instance,field))

    def set_filter(self, filter):
        if filter is not None:
            for field, w in self._widgets.items():
                if isinstance(w, ForeignKeyWidget):
                    try:
                        if isinstance(filter[field], w.model):
                            w.setData(filter[field])
                            w.setEnabled(False)
                        else:
                            for ffieldname, ffiltervalue in filter:
                                wid_filter = {}
                                if ffieldname in w.model.get_fields():
                                    wid_filter[ffieldname] = ffiltervalue
                                w.set_filter(wid_filter)
                    except KeyError:
                        pass

    def set_data_to_model(self):
        changed = False
        for field in self.fields:
            x = self.model.get_fields()[field]
            newvalue = self._widgets[field].getData()
            if newvalue!=getattr(self.model_instance, field):
                setattr(self.model_instance, field, newvalue)
                changed = True
        if changed:
            print "after change --------"
            print self.model_instance.__dict__
            self.model_instance.save()

    def accept(self):
        QDialog.accept(self)
        self.set_data_to_model()


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
