# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4 import QtCore, Qt



class AbstractModel(QtCore.QAbstractTableModel):

    def __init__(self, model, filter, fields=None, \
                 parent=None, blank_variant=False, \
                 blank_variant_verbose=u"<нет>", *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.model = model
        self.filter = filter
        self.blank_variant = blank_variant
        self.blank_variant_verbose = blank_variant_verbose


        if fields =="__unicode__":
            self._without_fields = True
        else:
            self.fields = fields
            self._without_fields = False

    def columnCount(self, parent):
        if self._without_fields:
            return 1
        else:
            return len(self.fields)


    def set_filter(self, filter):
        self.filter = filter
        self.modelReset.emit()


    def filtered_model(self):
        if self.filter is None:
            res = self.model.all()
        else:
            res = self.model.filter(**self.filter)
        if self.blank_variant:
            res = [None,] + res
        return res

    def get_model_instance_by_index(self, index):
        data = self.filtered_model()
        if not index.isValid():
            print index.row()
            return QtCore.QVariant()

        return data[index.row()]

    def get_model_instance_by_int_index(self, index):
        data = self.filtered_model()
        return data[index]

    def get_index_of_model(self, model):
        data = self.filtered_model()
        return data.index(model)

    def get_decorate(self, model_instance):
        """Returns (FontRole, BackgroundRole, ForegroundRole) for model_instance"""
        if model_instance.is_dumped() and model_instance.is_valid():
            return (QtCore.QVariant(), QtCore.QVariant(), QtCore.QVariant())
        else:
            font = QFont()
            font.setItalic(True)
            background = QColor(240, 128, 128)
            if not model_instance.is_valid():
                background = QColor("red")
            foreground = QtCore.QVariant()
            return (font, background, foreground)

    def rowCount(self, parent):
        count = len(self.filtered_model())

        return count

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            return QtCore.QVariant()
        elif orientation == QtCore.Qt.Horizontal:
            if self._without_fields:
                return QtCore.QString.fromUtf8(self.model.verbose_name())
            else:
                return QtCore.QString.fromUtf8(self.model.get_fields()[self.fields[section]].get_label())

class TableModel(AbstractModel):



    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        model_instance = self.get_model_instance_by_index(index)
        if role==QtCore.Qt.UserRole:
            return model_instance
        elif role==QtCore.Qt.FontRole:
            return self.get_decorate(model_instance)[0]
        elif role==QtCore.Qt.BackgroundRole:
            return self.get_decorate(model_instance)[1]
        elif role==QtCore.Qt.ForegroundRole:
            return self.get_decorate(model_instance)[2]
        elif role==QtCore.Qt.DisplayRole:
            if self._without_fields:
                return model_instance.__unicode__()
            else:
                field_raw_data = getattr(model_instance,self.fields[index.column()])
                result = self.model.get_fields()\
                        [self.fields[index.column()]].to_text(field_raw_data)
                return QtCore.QVariant(result)
        else:
            return QtCore.QVariant()


class ListModel(AbstractModel):
    def columnCount(self, parent):
        return 1

    def data(self, index, role):

        if not index.isValid():
            return QtCore.QVariant()
        else:
            model_instance = self.get_model_instance_by_index(index)
            if role==QtCore.Qt.UserRole:
                return model_instance
            elif role == QtCore.Qt.DisplayRole:
                if model_instance is None:
                    return self.blank_variant_verbose
                else:
                    return QtCore.QVariant(unicode(model_instance))
        return QtCore.QVariant()

class TreeModel(AbstractModel):
    def set_tree_structure(self, tree_structure):
        """@param tree: tree structure dictionary
        {name_of_foreignkey field: model class}"""
        self.__tree = tree_structure


    def parent(self, child):
        node = child.internalPointer()
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.child.index(parent)
        return self.createIndex(row, 0, parent)

    #def index(self, row, column, parent):
        #if not self.hasIndex(row, column, parent):
            #return QModelIndex()
        #if not parent.isValid():
            #parentItem = self.rootItem
        #else:
            #parentItem = parent.internalPointer()
        #childItem = parentItem.child[row]
        #if childItem:
            #return self.createIndex(row, column, childItem)
        #else:
            #return QtCore.QModelIndex()


    def data(self, index, role):

        if not index.isValid():
            return QtCore.QVariant()
        else:
            model_instance = self.get_model_instance_by_index(index)
            if role==QtCore.Qt.UserRole:
                return model_instance
            elif role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(unicode(model_instance))
        return QtCore.QVariant()





#from qtdjango.modelsmanager import ModelsManager

#ADDRESS = "http://127.0.0.1:8000"
#API_PATH= "/api/"
#mm = ModelsManager(ADDRESS, API_PATH, "/home/darvin/workspace/cryotec_service/cryotec_service", \
                              #["machines","actions","actiontemplates","clients",],
                              #("Action", "PAction",))

#current_module =__import__(__name__)



#mm.do_models_magic_with_module(current_module)

#print Machine.all()



#import os
#import sys
#from PyQt4.QtGui import *


#from PyQt4.QtCore import *
#from PyQt4.QtGui import *

#some = [
        #[1, "one", [2,3,4]],
        #[2, "tho", [8,]],
        #[3, "thee", [6,7]],
        #[4, "for", [5,]],
        #[5, "five", []],
        #[6, "six", []],
        #[7, "seven", []],
        #[8, "eignt", []],
       
       #]
#class TreeModel(QAbstractItemModel):
    #model = Machine
    #(("machinemark", MachineMark))
    #class zzNode(object):
        #def __init__(self, parent,  uid, txt, childs):
            #super(TreeModel.zzNode, self).__init__()
            #self.parent=parent
            #self.uid=uid
            #self.txt=txt
            #self.child = []
            #for a in childs:
                #self.child.append(TreeModel.zzNode(self, *some[a-1]))
        #def childCount(self):
            #return len(self.child)



    #def __init__(self, parent=None):
        #super(TreeModel, self).__init__(parent)
        #self.columns = 2
        #self.headers = ["key", "value"]
        #self.lastItems = [x for x in some if len(x[2])!=0]
        #print self.lastItems
        #self.rootItem=self.zzNode(None, some[0][0], some[0][1], some[0][2])

    #def rowCount(self, parent):
        #if parent.column() > 0: return 0
        #if not parent.isValid():
            #parentItem = self.rootItem
        #else:
            #parentItem = parent.internalPointer()
        #return parentItem.childCount()

    #def columnCount(self, parent):
        #return self.columns

    #def data(self, index, role):
        #if role == Qt.DisplayRole:
            #tmp=index.internalPointer().child
            #if index.column()==0:
                #return index.internalPointer().uid
            #else:
                #return QVariant(index.internalPointer().txt)
        #else:
            #return QVariant()

    #def headerData(self, section, orientation, role):
        #if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            #return QVariant(self.headers[section])
        #return QVariant()

    #def index(self, row, column, parent):
        #if not self.hasIndex(row, column, parent):
            #return QModelIndex()
        #if not parent.isValid():
            #parentItem = self.rootItem
        #else:
            #parentItem = parent.internalPointer()
        #childItem = parentItem.child[row]
        #if childItem:
            #return self.createIndex(row, column, childItem)
        #else:
            #return QtCore.QModelIndex()

    #def parent(self, child):
        #node = child.internalPointer()
        #if node is None:
            #return QModelIndex()
        #parent = node.parent
        #if parent is None:
            #return QModelIndex()
        #grandparent = parent.parent
        #if grandparent is None:
            #return QModelIndex()
        #row = grandparent.child.index(parent)
        #return self.createIndex(row, 0, parent)


#class TreeOfTableWidget(QTreeView):
    #def __init__(self):
        #super(TreeOfTableWidget, self).__init__()
        #self.setSelectionBehavior(QTreeView.SelectItems)
        #self.setUniformRowHeights(True)
        #model = TreeModel(self)
        #self.setModel(model)

#class MainForm(QMainWindow):
    #def __init__(self):
        #super(MainForm, self).__init__()
        #self.treeWidget = TreeOfTableWidget()
        #self.setCentralWidget(self.treeWidget)
        #QShortcut(QKeySequence("Escape"), self, self.close)
        #self.setWindowTitle("TreeViewExample")

#app = QApplication(sys.argv)




#form = MainForm()
#form.resize(750, 550)
#form.show()
#app.exec_()
