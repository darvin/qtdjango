'''
@author: darvin
This module must be imported from django enviroment
'''

from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.handler import AnonymousBaseHandler
from piston.utils import rc
from helpers import get_resource_name_for_model, get_all_models

from django.db import models

class CollectionHandler(AnonymousBaseHandler):
    exclude = ()
    allowed_methods = ('GET','POST')
    
    def has_model(self):
        return hasattr(self, 'model') or hasattr(self, 'queryset')




    def create(self, request, *args, **kwargs):
        if not self.has_model():
            return rc.NOT_IMPLEMENTED

        # get the actual data that wants to be created from the api request
        attrs = self.flatten_dict(request.POST)

        for field in self.model._meta.fields:
            if field.rel:
                # this is a ForeignKey (as far as I can tell... _meta isn't documented)
                # so we need to convert it to it's pk equivilent... there's most likely
                # a better way of doing this than hardcoding stuff...
                if field.name in attrs:
                    try:
                        attrs[field.name] =  field.rel.to.objects.get(\
                            **{field.rel.field_name: attrs[field.name]})
                    except:
                        pass


        try:
            inst = self.model.objects.get(**attrs)
            return rc.DUPLICATE_ENTRY
        except self.model.DoesNotExist:
            inst = self.model()
            inst = self.model(**attrs)
            inst.save()
            return inst
        except self.model.MultipleObjectsReturned:
            return rc.DUPLICATE_ENTRY

def get_url_pattens(app_list):
    """Gets app list returns urls patterns"""
    models = get_all_models(app_list, from_django=True)
    urlpatterns = [url(r"^"+get_resource_name_for_model(model),\
            Resource(type(model.__name__+"Handler", (CollectionHandler,), {"model":model})
                     )) for model in models]
 

    return patterns("", * urlpatterns)
