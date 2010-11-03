# -*- coding: utf-8 -*-
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QDesktopServices
from PyQt4 import QtCore
from qtdjango.models import Model
from PyQt4.QtWebKit import QWebView, QWebPage
#noinspection PyUnresolvedReferences
import PyQt4.QtNetwork
from PyQt4.QtCore import QSettings

__author__ = 'darvin'

class MultiModelView(object):
    models = None
    def __init__(self):
        for model in self.models:
            model.add_notify(self)



    def refresh(self):
        """Refreshs model"""
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
        QTreeWidget.__init__(self, *args, **kwargs)
        MultiModelView.__init__(self, *args, **kwargs)
        self.header().hide()
        self.refresh()
        self.currentItemChanged.connect(self.currentItemChange)


    def refresh(self):
        self.clear()
        self.__process_node(parenttreeitem=self)

    @QtCore.pyqtSlot("QTreeWidgetItem*", "QTreeWidgetItem*")
    def currentItemChange(self, current, previous):
        try:
            self.modelSelectionChanged.emit(current.model_instance)
        except AttributeError:
            self.modelSelectionCleared.emit()



class ModelInfoView(QWebView, MultiModelView):
    def __init__(self, *args, **kwargs):

        QWebView.__init__(self, *args, **kwargs)
        MultiModelView.__init__(self, *args, **kwargs)
        self.setHtml("")
#        if self.open_link_in_external_browser():
        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.linkClicked.connect(self.link_clicked)

    def link_clicked(self, link):
        print self.open_link_in_external_browser()
        if self.open_link_in_external_browser():
            QDesktopServices.openUrl(link)
        else:
            self.load(link)



    def refresh(self):
        try:
            self.modelChanged(self.model_instance)
        except AttributeError:
            pass

    def open_link_in_external_browser(self):
        return QSettings().value("open_links_in_external_browser", True).toBool()

    @QtCore.pyqtSlot(Model)
    def modelChanged(self, model):
        self.model_instance = model
        header1 = model.__class__.verbose_name()
        header2 = "" #unicode(model)
        fields = model.__class__.get_fields()
        field_text_values = {}
        for fieldname, field in fields.items():
            if not fieldname in ("user", "id", "extra_to_html"):
                field_text_values[fieldname] = []
                field_text_values[fieldname].append(field.verbose_name)
                field_text_values[fieldname].append(field.to_text(getattr(model, fieldname)))


        html = u""
        html += u"<h1>%s</h1><h2>%s</h2>" %(header1,header2)
        html += u"<br>".join([u"<b>%s:</b> <i>%s</i>"%(x[0], x[1]) for x in field_text_values.values()])

        html += "<br>" + model.extra_to_html()

        self.setHtml(html)

    @QtCore.pyqtSlot()
    def modelCleared(self):
        self.setHtml("")


