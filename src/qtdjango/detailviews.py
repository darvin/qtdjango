# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from baseview import BaseView

from widgets import *

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


