__author__ = 'darvin'

from django import forms

class MetaForm(forms.ModelForm):
   class Meta:
      pass


def create_form_type(model):
    """Builds form class from model
    @param model: Model class"""
    meta_type = type("Meta", (object,), {"model":model})
    form_type = type(model.__name__+"QtDjangoForm", (MetaForm,),\
                        {"Meta":meta_type})
    return form_type

