import json
from django.forms.models import ModelMultipleChoiceField
from django.http import QueryDict

__author__ = 'darvin'

from django import forms

class MetaForm(forms.ModelForm):
    class Meta:
        pass
    def __init__(self, *args, **kwargs):

        super(MetaForm, self).__init__(*args, **kwargs)


        data = {   }

        for field_name, field in self.fields.items():
            if field_name in self.data:
                if isinstance(field, ModelMultipleChoiceField):
                    data[field_name] = json.loads(self.data[field_name])
                else:
                    data[field_name] = self.data[field_name]
        self.data = data


    def clean(self):
        cleaned_data = self.cleaned_data

        return cleaned_data


def create_form_type(model):
    """Builds form class from model
    @param model: Model class"""
    meta_type = type("Meta", (object,), {"model":model})
    form_type = type(model.__name__+"QtDjangoForm", (MetaForm,),\
                        {"Meta":meta_type})
    return form_type

