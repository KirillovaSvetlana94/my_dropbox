from django.db import models
from django.contrib.auth.models import User
import swiftclient, swiftbrowser
from datetime import datetime
from django.conf import settings
from swiftbrowser.utils import get_temp_url
from django.shortcuts import render_to_response, redirect


USERNAME = settings.USER_SW
KEY = settings.KEY_SW
AUTH_URL = settings.AUTH_URL

DEFAULT_CONTAINER_TITLE = 'New Folder'


# Create your models here.
class Folder(models.Model):
	title = models.CharField(max_length=225, default=DEFAULT_CONTAINER_TITLE)
	date_created = models.DateTimeField(auto_now_add=True)
	parent_folder = models.ForeignKey("Folder", null=True, blank=True)
	user = models.ForeignKey(User)

	class Meta:
		ordering = ['-date_created']

	def __unicode__(self):
		return self.title


	username=USERNAME

	@classmethod
	def create_folder(csl, title, user, parent_folder=None):
		#user = User.objects.get(pk=csl.user)
		#user = User
		#user = csl.user
		try:
			folder = csl(title=title, parent_folder=parent_folder, user=user)
			folder.save()
			conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL)
			container_title = str(folder.id)
			conn.put_container(container_title)

		except swiftclient.ClientException:
			raise Exception("Access denied")

		return folder

	@classmethod	
	def view_your_folders(cls, pk):
		user = User.objects.get(id=pk)
		folders = Folder.objects.get(user=user)
		main_folders = []
		for fl in folders:
			if fl.parent_folder = None:
				main_folders.append(fl)

		return main_folders



	def get_files(self):
		try:
			conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL)
			container_title = str(self.id)

			_m, objects = conn.get_container(container_title)

		except swiftclient.ClientException:
			raise Exception("Access denied")

		return objects

	def get_temp_download_urls(self, file_title):
		#storage_url = request.session.get('storage_url', '')
		#auth_token = request.session.get('auth_token', '')
		container = str(self.id)
		try:
			conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL)
			url = get_temp_url(conn.get_auth()[0], conn.get_auth()[1], container, file_title, 7 * 24 * 3600)
			
		except swiftclient.ClientException:
			raise Exception("Access denied")

		return  redirect(url) 


	def get_subfolders(self):
		subfolders = Folder.objects.filter(parent_folder=self)
		return subfolders


	def delete_folder(self, **kwargs):
		try:
			conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL)
			container_title = str(self.id)
			_m, objects = conn.get_container(container=container_title)
			if len(objects)>0 :
				for obj in objects:
					conn.delete_object(container_title , obj['name'])
			conn.delete_container(container=container_title)

		except swiftclient.ClientException:
			raise Exception("Access denied")
		super(self.__class__, self).delete(**kwargs)


	def upload_file(self, file_title, file_contents, content_type):
		#print file_contents + "file contents"+ file_title+' '+str(content_type)
		try: 
			conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL) 
			cont_title = str(self.id)
			print cont_title
			conn.put_object(cont_title, file_title, file_contents, content_type=content_type)
		except swiftclient.ClientException:
			raise Exception("Access denied")

	def delete_file(self, filename):
		try:
			conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL)
			conn.delete_object(str(self.id), filename)
		except swiftclient.ClientException:
			raise Exception("Access denied")








 





