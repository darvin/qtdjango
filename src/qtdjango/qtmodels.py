from PyQt4.QtGui import *
from PyQt4 import QtCore, Qt



class AbstractModel(QtCore.QAbstractTableModel):

    def __init__(self, model, filter, fields=None, parent=None,  *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.model = model
        self.filter = filter
        self.fields = fields

    def set_filter(self, filter):
        self.filter = filter
        self.modelReset.emit()


    def filtered_model(self):
        if self.filter is None:
            return self.model.all()
        else:
            return self.model.filter(**self.filter)

    def get_qtdjango_model_by_index(self, index):
        data = self.filtered_model()
        if not index.isValid():
            print index.row()
            return QtCore.QVariant()
        return data[index.row()]

    def get_qtdjango_model_by_int_index(self, index):
        data = self.filtered_model()
        return data[index]

    def get_index_of_model(self, model):
        data = self.filtered_model()
        return data.index(model)



    def rowCount(self, parent):
        return len(self.filtered_model())

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            return QtCore.QVariant()
        elif orientation == QtCore.Qt.Horizontal:
            return QtCore.QString.fromUtf8(self.model.get_fields()[self.fields[section]].get_label())


class TableModel(AbstractModel):

    def columnCount(self, parent):
        return len(self.fields)


    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            return QtCore.QVariant()
        elif orientation == QtCore.Qt.Horizontal:
            return QtCore.QString.fromUtf8(self.model.get_fields()[self.fields[section]].get_label())


    def data(self, index, role):

        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()


        field_raw_data = getattr(self.get_qtdjango_model_by_index(index),self.fields[index.column()])
        result = self.model.get_fields()[self.fields[index.column()]].dump(field_raw_data)
        return QtCore.QVariant(result)


class ListModel(AbstractModel):
    def columnCount(self, parent):
        return 1

    def data(self, index, role):

        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()


        result = self.get_qtdjango_model_by_index(index).__unicode__()
        return QtCore.QVariant(result)


