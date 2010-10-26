# -*- coding: utf-8 -*-
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem
from PyQt4 import QtCore
from qtdjango.models import Model

__author__ = 'darvin'

class MultiModelView(object):
    pass




class ModelTreeWidgetItem(QTreeWidgetItem):
    def __init__(self,  parent, model_instance):
        super(ModelTreeWidgetItem, self).__init__(parent)
        self.model_instance = model_instance
        self.setText(0, unicode(self.model_instance))


class MultiModelTreeView(QTreeWidget, MultiModelView):
    tree_structure = None
    """@cvar: Tuple, structure of tree (("fieldname", ModelClass))"""
    item_class = ModelTreeWidgetItem
    """@cvar: Class of items"""
    modelSelectionChanged = QtCore.pyqtSignal([Model])
    modelSelectionCleared = QtCore.pyqtSignal()


    def __process_node(self, node=None, level=0, parenttreeitem=None):
        if node is None:
            subnodes = self.tree_structure[level][1].all()
        else:
            subnodes = self.tree_structure[level][1].filter(**{self.tree_structure[level-1][0]:node})

        result = []
        for subnode in subnodes:
            result.append(subnode)
            treeitem = self.item_class(parenttreeitem, model_instance=subnode)

            if level<len(self.tree_structure)-1:
                result.append(self.__process_node(subnode, level+1, treeitem))
        return result

    def __init__(self, *args, **kwargs):
        super(MultiModelTreeView,self).__init__(*args, **kwargs)
        self.__process_node(parenttreeitem=self)
        self.currentItemChanged.connect(self.currentItemChange)
        self.header().hide()

    @QtCore.pyqtSlot("QTreeWidgetItem*", "QTreeWidgetItem*")
    def currentItemChange(self, current, previous):
        self.modelSelectionChanged.emit(current.model_instance)
