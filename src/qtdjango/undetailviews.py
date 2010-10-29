# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4 import QtCore, Qt
from baseview import BaseView
from qtmodels import *
from models import Model

class UndetailView(BaseView):

    sort_by = None
    """@cvar sort by column"""

    def __init__(self, filter=None):
        BaseView.__init__(self)
        self.filter = filter

    def set_filter(self, filter):
        """Sets filter. Filter is dict"""
        self.filter = filter

    def clean(self):
        """Cleans temporary models of view"""
        pass



class UndetailWithButtonsView(QFrame, UndetailView):
    """Proxy class for UndetailView with buttons"""
    edit_dumped = True
    """@cvar: Allows edit and delete entries on server"""
    viewclass = None
    """@cvar: Class of detail view for editing entires"""
    buttons = {
               "delete": (True, u"Удалить"),
               "edit":(True,u"Редактировать"),
               "new":(False,u"Добавить"),
              }
    """@cvar: Buttons
    'name': (undumped only, 'caption'),"""

    edit_filtered_only = False
    """@cvar: allow edit only if view is filtered"""

    def __init__(self, filter=None, *args, **kwargs):
        """docstring for __init__"""
        QFrame.__init__(self)
        self.view = self.viewclass()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.view)
        self.buttonlayout = QHBoxLayout()
        self.layout.addLayout(self.buttonlayout)
        self._buttons = {}
        for button, (dumped_only, buttonname) in self.buttons.items():
            b = QPushButton(buttonname)
            self._buttons[button] = b
            self.buttonlayout.addWidget(b)
            #FIXME
            #l = lambda x: getattr(self.view,"model_"+button)()
            #print l
            #b.clicked.connect(l)
        self._buttons["edit"].clicked.connect(lambda x: self.view.model_edit())
        self._buttons["delete"].clicked.connect(lambda x: self.view.model_delete())
        self._buttons["new"].clicked.connect(lambda x: self.view.model_new())
        self.view.modelSelectionChanged.connect(self.modelSelectionChange)

        self.refresh_buttons_state()
        self.set_filter(filter)

    def get_buttons_state(self, model_selected=None):
        try:
            model_selected_undumped = not model_selected.is_dumped()
        except AttributeError:
            model_selected_undumped = True

        state = {}
        for button, (undumped_only, buttonname) in self.buttons.items():
            if self.edit_filtered_only and self.view.filter is None:
                state[button] = False
            else:
                if not self.edit_dumped and undumped_only and \
                   (not model_selected_undumped or model_selected is None):
                    state[button] = False
                else:
                    state[button] = True

        return state


    def refresh_buttons_state(self, model=None):
        """Disables buttons for edit, if not edit allowed"""
        current_state = self.get_buttons_state(model)
        for button, (undumped_only, buttonname) in self.buttons.items():
            self._buttons[button].setDisabled(not current_state[button])

    @QtCore.pyqtSlot(Model)
    def modelSelectionChange(self, model):
        self.refresh_buttons_state(model)

    def set_filter(self, filter):
        """Sets filter. Filter is dict"""
        self.view.set_filter(filter)
        self.refresh_buttons_state()

    def save(self):
        self.view.save()





class AbstactQtModelUndetailView(UndetailView, QAbstractItemView):
    def __init__(self, filter=None):
        QAbstractItemView.__init__(self)
        UndetailView.__init__(self, filter)
        self.qtmodel = self._qt_model_class(self.model, self.filter, self.fields)
        self.sortmodelproxy = QSortFilterProxyModel(parent=self)
        self.sortmodelproxy.setSourceModel(self.qtmodel)
        self.setModel(self.sortmodelproxy)
    def set_filter(self, filter):
        UndetailView.set_filter(self, filter)
        self.qtmodel.set_filter(self.filter)

    def create_detail_view(self, model_instance, filter=None):

        #t = type(self.model.__name__.upper() + "DetailView",\
                 #(DetailView,), {"model":model_to_edit})
        return self.detail_view(parent=self, model_instance=model_instance,\
                                filter=filter)

    @QtCore.pyqtSlot()
    def currentChanged (self, mi1, mi2):
        self.modelSelectionChanged.emit( self.qtmodel.data(\
                self.sortmodelproxy.mapToSource(mi1), QtCore.Qt.UserRole))


    def model_edit (self):
        dv = self.create_detail_view(\
                    self.qtmodel.data(\
                            self.sortmodelproxy.mapToSource(self.currentIndex()),\
                            QtCore.Qt.UserRole))
        dv.show()

    def model_delete (self):
        m = self.qtmodel.data(\
                            self.sortmodelproxy.mapToSource(self.currentIndex()),\
                            QtCore.Qt.UserRole)
        m.delete()

    def create_model_instance(self):
        return self.model.new()

    def model_new (self):
        new_model = self.create_model_instance()
        dv = self.create_detail_view(model_instance=new_model, filter=self.filter)
        result = dv.exec_()
        if result==QDialog.Accepted:
            pass
        elif result==QDialog.Rejected:
            new_model.delete()

    def refresh(self):
        self.qtmodel.reset()

    def save(self):
        """Does nothing, all changes saves instantly"""
        pass

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
        self.setSortingEnabled(True)
#        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().hide()
        if self.sort_by:
            if self.sort_by[0]=="-":
                sort_order = QtCore.Qt.DescendingOrder
                sort_by = self.sort_by[1:]
            else:
                sort_order = QtCore.Qt.AscendingOrder
                sort_by = self.sort_by

            self.sortByColumn(self.fields.index(sort_by), sort_order)






class TreeView(QTreeView, AbstactQtModelUndetailView):
    _qt_model_class = TreeModel
    modelSelectionChanged = QtCore.pyqtSignal([Model]) ##dont work when in
                                                        #father class

    modelSelectionCleared = QtCore.pyqtSignal()
    tree_structure = {}
    """@cvar: Dict of tree structure {fk field name: model class}"""

    def __init__(self, filter=None):
        QTreeView.__init__(self)
        AbstactQtModelUndetailView.__init__(self, filter)
        self.qtmodel.set_tree_structure(self.tree_structure)
