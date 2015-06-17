from tastypie import fields, http
from tastypie.resources import Resource, ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from .models import Folder 
from django.conf.urls import url
from tastypie.utils import trailing_slash
import datetime
import base64
import simplejson as json
import swiftclient

class ContainerResource(ModelResource):
	class Meta:
		queryset = Folder.objects.all()
		resource_name = 'storage'
		detail_allowed_methods = ['get', 'post']

	def prepend_urls(self):
		return [
			url(
				r"^(?P<resource_name>%s)/(?P<pk>\d+)/download%s$" %
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('download'),
				name='api_download'
			),
			url(
				r"^(?P<resource_name>%s)/(?P<pk>\d+)/upload%s$" %
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('upload'),
				name='api_upload'
			),
		]

	# def prepend_url(self):
	# 	return [
	# 		url(
	# 			r"^(?P<resource_name>%s)/(?P<pk>\d+)/upload%s$"%
	# 				(self._meta.resource_name, trailing_slash()),
	# 								self.wrap_view('upload'),
	# 								name= 'api_upload' ###?????????->?????
	# 		),
	# 		url(
	# 			r"^(?P<resource_name>%s)/(?P<pk>\d+)/download%s$" %
	# 			(self._meta.resource_name, trailing_slash()),
	# 				self.wrap_view('download'),
	# 				name='api_download'
	# 		),
	# 	]

	def upload(self, request, **kwargs):
		#print "Hello"
		data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
		file_contents = base64.b64decode(data['uploaded_file'])
		filename = data['filename']
		content_type = data['content_type']
		folder_id = kwargs.get('pk')
		folder = Folder.objects.get(pk=folder_id)
		try:
			folder.upload_file(file_title=filename, file_contents=file_contents, 
				content_type=content_type)

		except swiftclient.ClientException:
				return http.HttpUnauthorized("You are not authorized in stackswift service, \
					please, make sure that you add your username and key to your settings")

		return self.create_response(
		 	request,
		 	data,
		 	response_class=http.HttpAccepted
		 )

	def download(self, request, **kwargs):
		filename = kwargs.get('filename')
		print 'filename:'+filename
		folder_id = kwargs.get('cont_title')
		folder = Folder.objects.get(id=folder_id)
		try:
			temp_url =folder.get_temp_download_url(request=request, file_title=filename)
		except swiftclient.ClientException:
			return http.HttpUnauthorized("You are not authorized in stackswift service, \
				please, make sure that you add your username and key to your settings")

		return self.create_response(
			request,
				temp_url 
			,
			response_class=http.HttpAccepted
		)




