'''
@author: darvin
This module must be imported from django enviroment
'''


from piston.handler import AnonymousBaseHandler
from piston.utils import rc
from piston.utils import validate

from forms import create_form_type
import qtdjango
from django.conf import settings

class InfoHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    models = []

    @staticmethod
    def create_model_info(model):
        fields = {}
        for field in model._meta.fields:
            try:
                f = {}
                f["type"]=field.__class__.__name__
                fields[field.name] = f
            except AttributeError:
                pass

        info = {"name":model.__name__, \

                "fields":fields,\
                }

        try:
            info["dump_order"]=model.dump_order
        except AttributeError:
            pass
        return info

    @classmethod
    def set_models(cls, models):
        for model in models:
            cls.models.append(cls.create_model_info(model))

    def read(self, request):
        d = {
            "qtdjango_version":qtdjango.__version__,
            "qtdjango_apps_setting":getattr(settings, "QTDJANGO_APPS" ),
            "models":self.models
        }
        return d



class MetaHandler(AnonymousBaseHandler):
    exclude = ()
#    fields = ("machinemark",)
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


def create_handler_type(model):
    """Builds handler class from model
    @param model: Model class"""
    f = []
    for field in model._meta.fields:
        f.append(field.name)
    try:
        for method in model.include_methods_results:
            f.append(method)
    except AttributeError:
        pass
    for field in model._meta.many_to_many:
        f.append(field.name)
    handler_type = type(model.__name__+"Handler", (MetaHandler,),\
                        {"model":model, "fields":f})
    valid_decor = validate(create_form_type(model))
    handler_type.create = valid_decor(handler_type.create)



    return handler_type