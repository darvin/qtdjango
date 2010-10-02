
# -*- coding: UTF-8 -*-

'''
@author: darvin
'''

from inspect import getmro




def istype(obj, typename):
    try:
        return typename in [clsobj.__name__ for clsobj in getmro(obj.__class__)]
    except AttributeError:
        return False

class Field(object):
    
    widget = None
    
    def __init__(self, verbose_name=None, *args, **kwargs):
        try:
            self.verbose_name = verbose_name
        except IndexError:
            pass

    def load(self, data):
        return data
    
    def dump(self, data):
        return data
    
    def blank(self):
        return None
    
    def get_label(self):
        try:
            return self.verbose_name
        except AttributeError:
            return "verbose name not defined"


class IdField(Field):
    def load(self, data):
        return int(data)

class TextField(Field):
    pass

class DateField(Field):
    pass

class DateTimeField(DateField):
    pass

class CharField(Field):
    pass



class BooleanField(Field):
    pass

class EmailField(CharField):
    pass


class FileField(CharField):
    pass

class IntegerField(Field):
    def load(self, data):
        return int(data)
    
    def dump(self, data):
        return int(data)

class PositiveIntegerField(IntegerField):
    pass

class ForeignKey(Field):
    
    def load(self, data):
        if data is not None:
            if self.model.loaded:
                return self.model.get(data["id"])
            else:
                return data
        else:
            return None
        
    
    def dump(self, data):
        return unicode(data)
    
    def __init__(self, model, verbose_name=None, *args, **kwargs):
        super(ForeignKey, self).__init__(verbose_name=verbose_name, *args, **kwargs)
        self.model = model
#        self.model.load()
        
        
#        self.model.__setattr__("foreing_key_model_"+kwargs["self"].__name__, kwargs["self"])






from connection import Connection


class ResourceNameError(Exception):
    pass


class Model(object):
    '''
    classdocs
    '''
    resource_name = None
    """this is table of resource names of models"""
    
    loaded = False

    objects = []


    @classmethod
    def load(cls):
        if not cls.loaded:
            if cls.resource_name is None:
                raise ResourceNameError
            
            
            
            cls.id = IdField("Id")
            raw = Connection.get(cls.resource_name)

            cls.objects = [cls(**x) for x in raw]
            cls.loaded = True
            
#    #Fixme
    @classmethod
    def refresh_foreing_keys(cls):
        for obj in cls.objects:
            for fieldname in dir(cls):
                if isinstance(getattr(cls,fieldname), ForeignKey):
                    if not istype(getattr(obj, fieldname), "Model"):
                        setattr(obj, fieldname, getattr(cls, fieldname).load(getattr(obj, fieldname)))
      
      
    @classmethod
    def printall_foreing_keys(cls):
        for obj in cls.objects:
            for fieldname in dir(cls):
                if isinstance(getattr(cls,fieldname), ForeignKey):
                    print getattr(obj, fieldname)
                    
    @classmethod
    def dump(cls):
        raise NonImplementedError
    
    @classmethod  
    def all(cls):
        return cls.filter()
    
    @classmethod    
    def new(cls, **kwargs):
        return cls(**kwargs)
    
    @classmethod
    def filter(cls, **kwargs):
        return [x for x in cls.objects if x.is_filtered(**kwargs)]
                                                        
    
    @classmethod
    def get(cls, id):
        res = cls.filter(id=id)
        if len(res)==1:
            return res[0]
            
#    def foreign_set(self, setname):
#        try:
#            fclass = "foreing_key_model_"+setname
#        except KeyError:
#            print setname
#            print globals()
#            pass 
#        return fclass.filter(\
#                    **{self.__class__.__name__.lower():self})
    
    @classmethod
    def get_fields(cls):
        """
        Returns dict of class Fields
        """
        f = {}
        for fieldname in dir(cls):
            if istype(getattr(cls, fieldname), "Field"):
                f[fieldname] = getattr(cls, fieldname)
        return f

    
    def is_filtered(self, **kwargs):
        for field in kwargs:
            try:
                if getattr(self, field)!=kwargs[field]:
                    return False
            except KeyError:
                if "__" in field:
                    keymodel, keyfield = field.split("__")
                    if getattr(getattr(self,keymodel),keyfield)!=kwargs[field]:
                        return False
                else:
                    print field
                    raise KeyError
        return True
    
    def __init__(self, **initdict):
        super(Model,self).__init__()
        
        
        for fieldname, field in self.__class__.get_fields().items():
#            try:
                setattr(self, fieldname, field.load(initdict[fieldname]))
#            except KeyError:
#                setattr(self, fieldname, field.blank)
#     
     
    def validate(self):
        pass
    
    def save(self):
        self.validate()
        
        dubl = self.get(self.id)
        
        if dubl is None:
            self.objects.append(self)
        self.undumped = True
    
    def __unicode__(self):
        return "default unicode method"



class User(Model):
    #Todo: implement django behavoir
    resource_name = "django/users/"
    username = CharField() 
    first_name = CharField()
    
if __name__=="__main__":
    
    
#    from cryotec_service.machines.models import *
#    from cryotec_service.clients.models import *
#    Machine.load()
# 
#    print Machine.fields
#    
#    
#    print Machine.resource_name
#    print Client.resource_name
#    print Client.get(1).name
#    print Machine.get(1).serial
#    print Machine.get(1).motohours
    pass