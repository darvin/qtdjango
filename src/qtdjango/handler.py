import warnings

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, FieldError
from django.conf import settings
from django.db.models.query import QuerySet
from django.core.paginator import Paginator, InvalidPage, EmptyPage


from utils import rc, has_model, flatten_dict
from responses import *

class BaseHandler(object):
	"""
	Basehandler that gives you CRUD for free.
	You are supposed to subclass this for specific
	functionality.
	
	All CRUD methods (`read`/`update`/`create`/`delete`)
	receive a request as the first argument from the
	resource. Use this for checking `request.user`, etc.
	"""
	#__metaclass__ = HandlerMetaClass
	
	allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
	anonymous = is_anonymous = False
	exclude = ( 'id', )
	fields =  ( )
	
	def flatten_dict(self, dct):
		return flatten_dict(dct)
	
	def has_model(self):
		return hasattr(self, 'model') or hasattr(self, 'queryset')

	def queryset(self, request):
		return self.model.objects.all()
	
	def value_from_tuple(tu, name):
		for int_, n in tu:
			if n == name:
				return int_
		return None
	
	def _querydict_to_dict(self, q):
		"""
		Use on e.g. request.GET in order to get a python dict suitable for **kwargs-ing into a queryset filter.
		"""
		d = {}
		for k in q.keys():
			d[str(k)] = q[k]	# str() is necessary, apparently - presumably because normal kwargs are ascii
		return d
		
	def exists(self, **kwargs):
		if not self.has_model():
			raise NotImplementedError
		
		try:
			self.model.objects.get(**kwargs)
			return True
		except self.model.DoesNotExist:
			return False
	
	@has_model
	def read(self, request, format, *args, **kwargs):

		pkfield = self.model._meta.pk.name

		if pkfield in kwargs:
			try:
				return self.queryset(request).get(pk=kwargs.get(pkfield))
			except ObjectDoesNotExist:
				return HttpResponseNotFound('The object you requested could not be found')
			except MultipleObjectsReturned: # should never happen, since we're using a PK
				return HttpResponseBadRequest('More than one object was found!')
		else:
			return self.queryset(request).filter(*args, **kwargs)
	
	@has_model
	def create(self, request, format, *args, **kwargs):
		attrs = self.flatten_dict(request.POST)
		
		try:
			inst = self.queryset(request).get(**attrs)
			return HttpResponseDuplicateEntry('This entry already exists!')
		except self.model.DoesNotExist:
			inst = self.model(**attrs)
			inst.save()
			return inst
		except self.model.MultipleObjectsReturned:
			return HttpResponseDuplicateEntry('This entry already exists, and more than once to boot!')
	
	@has_model
	def update(self, request, format, *args, **kwargs):
		pkfield = self.model._meta.pk.name

		if pkfield not in kwargs:
			# No pk was specified
			return HttpResponseBadRequest('Please specify a unique identifier for the entry to update')

		try:
			inst = self.queryset(request).get(pk=kwargs.get(pkfield))
		except ObjectDoesNotExist:
			return HttpResponseBadRequest('The object you requested to update could not be found')
		except MultipleObjectsReturned: # should never happen, since we're using a PK
			return HttpResponseBadRequest('The unique identifier you supplied returned more than one entry!')

		attrs = self.flatten_dict(request.POST)
		for k,v in attrs.iteritems():
			setattr( inst, k, v )

		inst.save()
		return HttpResponseAllOK()
	
	@has_model
	def delete(self, request, format, *args, **kwargs):
		try:
			inst = self.queryset(request).get(*args, **kwargs)

			inst.delete()

			return HttpResponseDeleted()
		except self.model.MultipleObjectsReturned:
			return HttpResponseDuplicateEntry('The unique identifier you supplied returned more than one entry!')
		except self.model.DoesNotExist:
			return HttpResponseGone('This entry already does not exist')
		
class AnonymousBaseHandler(BaseHandler):
	"""
	Anonymous handler.
	"""
	is_anonymous = True
	allowed_methods = ('GET',)

"""
The following two classes subclass BaseHandler to form classes for handling
the django Model in two different ways: as a collection (CollectionHandler)
and as a member (MemberHandler).

A collection basically corresponds to a queryset, e.g. Person.objects.all(),
whereas a member corresponds to a single Model instance, e.g. "Joe Bloggs".

An easy analogy can be drawn with Django's generic object_list (a
collection) and object_detail (a member).

A pretty good article on collections and members: <http://www.projectzero.org/sMash/1.0.x/docs/zero.devguide.doc/zero.resource/rest-api.html>
For a table of how HTTP methods are interpreted for collections and members: <http://en.wikipedia.org/wiki/REST#RESTful_web_services>
"""

class CollectionHandler(BaseHandler):
	"""
	This class implements appropriate definitions of read, create, update,
	and delete for the interpretation of the resource as a COLLECTION.
	"""
	
	class ClientQueryVocabulary:
		"""
		Represents a vocabulary used by a client to indicate things like pagination and sorting.
		There seems to be no standardization here, so for every different possible client we create a vocab.
		"""
		def __init__(self,
				paginate_page_name,					# Name of the GET attribute indicating which page we want
				paginate_results_per_page_name,		# Name of the GET attribute indicating how many results we want per page
				
				sort_field_name,					# Name of the GET attribute indicating which column/field to sort by
				sort_order_name,					# Name of the GET attribute indicating the order in which we should sort
				
				query_name,							# Name of the GET attribute indicating a query to run
				query_type							# Type of the above query
				):
			self.paginate_page_name = paginate_page_name
			self.paginate_results_per_page_name = paginate_results_per_page_name
			
			self.sort_field_name = sort_field_name
			self.sort_order_name = sort_order_name
			
			self.query_name = query_name
			self.query_type = query_type

	client_query_vocabularies = {
		'flexigrid':	ClientQueryVocabulary('page', 'rp', 'sortname', 'sortorder', 'query', 'qtype'),		# http://www.flexigrid.info/
		}
	
	client_query_vocabulary = client_query_vocabularies['flexigrid']	# In specifying this default I'm obviously partial.
	
	paginate = True	# If we support pagination
	sort = True	# Whether we support a specified sort order
	query = True	# Whether to let the client specify a "query" attribute in the GET string
	
	_sort_order_name_map = {	# For normalizing the possible client options for specifying sort order.  This is just prepended to the order_by() argument.
		'ASC': 			'',
		'asc': 			'',
		'ASCENDING':	'',
		'ascending':	'',
		
		'DESC':			'-',
		'desc':			'-',
		'DESCENDING':	'-',
		'descending':	'-'
		}
	
	@has_model
	def read(self, request, format, *args, **kwargs):
		"""
		Get an entire collection from the model, filtered by the arguments given.
		"""
		request.GET = request.GET.copy()	# make mutable
		
		if self.paginate:
			# pop them from GET so they don't interact with field names
			try:
				page_no = request.GET[self.client_query_vocabulary.paginate_page_name]
				del request.GET[self.client_query_vocabulary.paginate_page_name]
			except KeyError:
				page_no = None
			
			try:
				results_per_page = request.GET[self.client_query_vocabulary.paginate_results_per_page_name]
				del request.GET[self.client_query_vocabulary.paginate_results_per_page_name]
			except KeyError:
				results_per_page = None
			
			# make sure they can be cast to integers
			try:
				page_no = int(page_no)
			except ValueError:
				return HttpResponseBadRequest("The page number you specified, '%s', did not resolve to an integer" % page_no)
			
			try:
				results_per_page = int(results_per_page)
			except ValueError:
				return HttpResponseBadRequest("The results per page you specified, '%s', did not resolve to an integer" % results_per_page)
			
			# we now leave to create the query before paginating
		
		if self.sort:
			# pop them from GET so they don't interact with field names
			try:
				sort_field = request.GET[self.client_query_vocabulary.sort_field_name]
				del request.GET[self.client_query_vocabulary.sort_field_name]
			except KeyError:
				sort_field = None
			
			try:
				sort_order = request.GET[self.client_query_vocabulary.sort_order_name]
				del request.GET[self.client_query_vocabulary.sort_order_name]
			except KeyError:
				sort_field = None
			
			try:
				sort_order = self._sort_order_name_map[sort_order]
			except KeyError:
				return HttpResponseBadRequest("The sort order you specified, '%s', was not recognized" % sort_order)
			
			# we now leave to create the query; then we sort it
		
		if self.query:
			try:
				query_to_execute = request.GET[self.client_query_vocabulary.query_name]
				del request.GET[self.client_query_vocabulary.query_name]
			except KeyError:
				query_to_execute = None
			
			try:
				query_type = request.GET[self.client_query_vocabulary.query_type]
				del request.GET[self.client_query_vocabulary.query_type]
			except KeyError:
				query_type = None
			
			# ... IMPLEMENT THIS.
		
		try:
			queryset = self.queryset(request).filter(**self._querydict_to_dict(request.GET))
		except FieldError, e:
			return HttpResponseBadRequest('The query you provided did not resolve to known field names: %s' % e)
		except ValueError, e:
			return HttpResponseBadRequest('One or more values did not validate: %s' % e)
		
		if self.sort and sort_field and (sort_order != None):
			# The user wants to sort the query; do it
			queryset = queryset.order_by(sort_order + sort_field)
		
		if self.paginate and page_no and results_per_page:
			# the user wants to paginate the queryset; do it
			try:
				queryset = Paginator(queryset, results_per_page).page(page_no).object_list	# Use the standard Django paginator
			except (InvalidPage, EmptyPage):
				return HttpResponseBadRequest('The pagination you specified was not valid')
		
		return queryset
	
	@has_model
	def create(self, request, format, *args, **kwargs):
		"""
		Using the data in POST, create a new member of this collection,
		and return it.
		"""
		try:
			inst = self.queryset(request).get(**request.data)
			return HttpResponseDuplicateEntry('The data you specified matches an existing entry')
		except self.model.DoesNotExist:
			if self.form:
				form = self.form(**request.data)
				if form.is_valid():
					return form.save()
				else:
					return HttpResponseBadRequest('Your data did not validate for this entry type')
			else:
				inst = self.model(**request.data)
				inst.save()
				return inst
		except self.model.MultipleObjectsReturned:
			return HttpResponseDuplicateEntry('The data you specified matches many existing entries!')
	
	@has_model
	def update(self, request, format, *args, **kwargs):
		"""
		Meaning defined as "replace the entire collection with another collection".
		"""
		pass
		"""
		The difference between this and every other REST method is that the 
		client is giving us the data of an entire COLLECTION rather than one member
		(or filtering data that looks like it could specify a member).
		
		Therefore we have to decide how data in request.POST or request.PUT should
		be structured in order to specify a collection.
		
		This is easy if the client is giving us structured JSON or XML data,
		which is capable of a sensible hierarchical structure.
		
		However, if the client wants to use standard url-encoding, we have to fall back
		on that trick used in django formsets (and elsewhere), like so:
		
		name_0=james&age_0=22&name_1=jesper&age_1=25&name_2= ...
		
		IMPLEMENT THIS.
		"""
	
	@has_model
	def delete(self, request, format, *args, **kwargs):
		"""
		Delete the entire collection (filtered by the parameters given).
		THIS IS DANGEROUS, DUDE!
		"""
		self.queryset(request).delete()
		return HttpResponseAllOK('All entries in this collection were deleted')
	
class MemberHandler(BaseHandler):
	"""
	This class implements appropriate definitions of read, create, update,
	and delete for the interpretation of the resource as a MEMBER.
	"""
	
	def _inst(self, request, kwargs):
		"""
		Get the django Model instance object specified by the client's request data.
		"""
		try:
			member_pk = kwargs[self.pkfield]
		except KeyError: # The client has not specified the primary key of this member.
			return HttpResponseBadRequest('Please specify a value for "%(identifier)s"' % { 'identifier': self.pkfield })
		else:
			try:
				return self.queryset(request).get(**{self.pkfield: member_pk})
			except ObjectDoesNotExist:
				return HttpResponseNotFound('The entry you requested could not be found')
			except MultipleObjectsReturned: # should never happen, since we're using a PK
				return HttpResponseBadRequest('The unique identification you specified returned more than one entry!')
		
	@has_model
	def read(self, request, format, *args, **kwargs):
		"""
		Get a single member, identified by primary key, and return it.
		"""
		return self._inst(request, kwargs)
	
	@has_model
	def create(self, request, format, *args, **kwargs):
		"""
		Returns 400 Bad Request.
		
		Method POST on an individual member doesn't make much sense in the abstract.
		Wikipedia says this should "[treat] the addressed member as a collection 
		in its own right and [create] a new subordinate of it".
		
		If you want this functionality then you'll have to implement it by
		overriding this function.
		"""
		return HttpResponseBadRequest('Performing a POST request on this handler has not been implemented')
	
	@has_model
	def update(self, request, format, *args, **kwargs):
		"""
		Update the addressed member of the collection or create it with the specified ID.
		"""
		inst = self._inst(request, kwargs)
		
		if not isinstance(inst, QuerySet):  # The request failed to generate a unique object.
			return inst # In this case, inst is an HttpResponse message.
		
		if self.form:
			form = self.form(request.data, instance=inst)
			if form.is_valid():
				form.save()
				return HttpResponseAllOK()
			else:
				return HttpResponseBadRequest('Your data did not validate')
		else:
			for k,v in request.data.iteritems():
				setattr( inst, k, v )
			inst.save()
			return HttpResponseAllOK()
	
	@has_model
	def delete(self, request, format, *args, **kwargs):
		"""
		Delete the addressed member of the collection.
		"""
		self._inst(request, kwargs).delete()
		return HttpResponseDeleted()

from django.db.models.fields import ( AutoField, CharField, TextField,
	FloatField, SlugField, EmailField, IntegerField, BooleanField,
	DateField, DateTimeField )

class SchemaHandler(BaseHandler):
	"""
	This class implements just one method: GET.  This returns a schema for 
	the associated model.
	"""
	_map = {
		AutoField: 'integer',
		CharField: 'string',
		TextField: 'string',
		FloatField: 'number',
		SlugField: 'string',
		EmailField: 'string',
		IntegerField: 'integer',
		BooleanField: 'boolean',
		DateField: 'string',
		DateTimeField: 'string'
		}
	
	@has_model
	def read(self, request, format, *args, **kwargs):
		"""
		In most cases, these methods can return, say, a QuerySet without any 
		concern for the way in which it is going to be formatted (JSON, XML, etc).
		This is not the case here: if the user requests JSON, we return a JSON schema;
		if XML, an XML schema, which differ in more complex ways than structure.
		"""
		if format == 'json':
			"""
			This schema format is based on the description at <http://json-schema.org/>
			"""
			schema = {
				"description": unicode(self.model._meta.verbose_name),
				"properties": {}
				}
			for field in self.model._meta.fields:
				f = {}
				cls = field.__class__
				try:
					f["type"] = self._map[cls]
				except KeyError:	# We don't know about this field type: ignore it
					pass
				else:
					# Go through different field types and populate the schema with things we can find about the field
					if cls == CharField:
						f["maxLength"] = field.max_length
				schema["properties"][field.name] = f
			return schema
		else:
			raise NotImplementedError("the requested schema format has not been implemented")

model_fields = {}
model_exclude_fields = {}

class HandlerFactoryMetaClass(type):
	def __new__(cls, name, bases, attrs):
		new_cls = type.__new__(cls, name, bases, attrs)
		if hasattr(new_cls, 'model'):
			if hasattr(new_cls, 'fields'):
				model_fields[new_cls.model] = new_cls.fields
			if hasattr(new_cls, 'exclude'):
				model_exclude_fields[new_cls.model] = new_cls.exclude
		return new_cls

class ModelHandlerFactory(object):
	__metaclass__ = HandlerFactoryMetaClass
	@classmethod
	def CollectionHandler(cls):
		class NewHandler(CollectionHandler):
			model = cls.model
			form = cls.form
			
		return NewHandler
	
	@classmethod
	def MemberHandler(cls):
		try:
			identifier = cls.identifier
		except AttributeError:
			identifier = cls.model._meta.pk.name
		
		class NewHandler(MemberHandler):
			model = cls.model
			form = cls.form
			pkfield = identifier
		return NewHandler
	
	@classmethod
	def SchemaHandler(cls):
		class NewHandler(SchemaHandler):
			model = cls.model
		return NewHandler
