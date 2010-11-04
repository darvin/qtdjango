# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from baseview import BaseView

from widgets import *

class DetailView(QDialog, BaseView):
    fieldwidgets_dict = {TextField:TextEditWidget,
                         IdField:IdLabelWidget,
                       CharField:LineEditWidget,
                       IntegerField:SpinBoxWidget,
                       ForeignKey:ForeignKeyWidget,
                       DateTimeField:DateTimeEditWidget,
                       DateField:DateTimeEditWidget,
                       BooleanField:CheckBoxWidget,
                       }

    inline_views = ()
    """@cvar: Tuple of inline views. ((InlineViewClass, "filter_field", "Caption"),)"""

    def __init__(self, model_instance, parent=None, filter=None,**kwargs):
        QDialog.__init__(self, parent, **kwargs)
        BaseView.__init__(self, **kwargs)

        self.setWindowTitle(u"%s: редактирование" % self.model.verbose_name())

        self.model_instance = model_instance

        self.formlayout = QFormLayout()
        self._widgets={}
        self.fields = [field for field in self.fields\
                       if not getattr(self.model,field).is_read_only_in(self.model)]
        for field in self.fields:
            x = getattr(self.model,field)
            try:
                self._widgets[field] = self.widgets[field]
            except KeyError:
                try:
                    self._widgets[field] = \
                            self.fieldwidgets_dict[x.__class__](x)
                except KeyError:
                    self._widgets[field] = LabelWidget() ##FIXME!
            self.formlayout.addRow(x.get_label(), self._widgets[field])
        self.get_data_from_model()

        #then initialise inline views:
        self._inline_views = []
        for inline_view_class, inline_filter_field, inline_caption in self.inline_views:
            v = inline_view_class(filter={inline_filter_field:self.model_instance})
            #v.set_filter({inline_filter_field:self.model_instance})
            self._inline_views.append(v)
            self.formlayout.addRow(QLabel(inline_caption))
            self.formlayout.addRow(v)


        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                      | QDialogButtonBox.Cancel)
        Qt.QObject.connect(buttonBox, Qt.SIGNAL("accepted()"), self, Qt.SLOT("accept()"));
        Qt.QObject.connect(buttonBox, Qt.SIGNAL("rejected()"), self, Qt.SLOT("reject()"));

        v_layout = QVBoxLayout(self)
        v_layout.addLayout(self.formlayout)
        v_layout.addWidget(buttonBox)


        self.setLayout(v_layout)
        self.set_filter(filter)



    def get_data_from_model(self):
        for field in self.fields:
            self._widgets[field].setData(getattr(self.model_instance,field))

    def set_filter(self, filter):
        print "filter ", filter
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
            self.model_instance.save()

        ##save inline views
        for v in self._inline_views:
            v.save()

    def validate(self):

        invalids = self.model_instance.validate()

        result = True
        for fieldname, value in invalids.items():
            if value is not None:
                field = getattr(self.model, fieldname)
                result = False
                newtext = field.get_label() +" <br> <i><font color=red>"+ value +"</color></i>"
                self.formlayout.labelForField(self._widgets[fieldname]).setText(newtext)


        return result

    def accept(self):
        self.set_data_to_model()

        if self.validate():
            QDialog.accept(self)


    def reject(self):
        for v in self._inline_views:
            v.clean()
        QDialog.reject(self)


