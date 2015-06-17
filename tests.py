from django.test import TestCase, TransactionTestCase
from tastypie.test import ResourceTestCase, TestApiClient
from django.db import models
from django.contrib.auth.models import User
import swiftclient
from datetime import datetime
from django.conf import settings
from dropbox.models import Folder, DEFAULT_CONTAINER_TITLE,  User
import os



USERNAME = settings.USER_SW
KEY = settings.KEY_SW
AUTH_URL = settings.AUTH_URL

# Create your tests here.

class FolderTestCases(TestCase):
	fixtures = ['app_data.json','user_data.json']

	def setUp(self):
		super(self.__class__, self).setUp()

	"""def test_delete_folder(self):
	  	try:
	  		conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL)
	  		_m, objects = conn.get_container(container='9')
	  		if len(objects)>0 :
	  			for obj in objects:
	  				conn.delete_object('9' , obj['name'])
	  		conn.delete_container(container='9')

	  	except swiftclient.ClientException:
	  		raise Exception("Access denied")	
	"""
	def test_create_folder(self):
		user = User.objects.get(id='1')
		folder1 = Folder.create_folder(title='New Folder',  user=user)
		folder1.save()
		print "folder1 id= ", folder1.id
		#self.assertEqual(folder1.title, DEFAULT_CONTAINER_TITLE)
		try: 
			conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL)
			_m, objects = conn.get_container(str(folder1.id))
			self.assertEqual(len(objects), 0) 
		except swiftclient.ClientException:
			raise Exception("Access denied")
		else: 
			folder1.delete_folder()
			user.delete()

	def test_create_subfolder(self):
	 	user=User.objects.get(id='1')
	 	parent_folder = Folder.objects.get(id='8')
	 	subfolder = Folder.create_folder(title='Subfolder', parent_folder=parent_folder, user=user)

	 	######
	 	parent_folder2  =Folder.objects.get(id='8')
	 	subfolder2 = parent_folder2.folder_set.get(title='Subfolder')
		self.assertEqual(subfolder.id, subfolder2.id)

		#### using get_subfolders() method
		self.assertEqual(subfolder, parent_folder2.get_subfolders().get(title='Subfolder')) 


		subfolder.delete_folder()
		

	def test_upload_file(self):
		file_path = '/home/sveta/Documents/esenin.jpg'
		from mimetypes import MimeTypes
		mime = MimeTypes()
		mime_type = mime.guess_type(file_path)
		my_file = open(file_path, 'rb').read()
		
		folder = Folder.objects.get(id = '8')	
		user = User.objects.get(id='1')
		
		#print folder.id
		folder.upload_file(file_title='esenin.jpg', file_contents=my_file, content_type=mime_type)

		cont_title = str(folder.id)
		try:
			conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL)
			_m, objects = conn.get_container(cont_title)
			self.assertEqual(len(objects), 2)

			folder.delete_file(filename='esenin.jpg')
			_m, objects = conn.get_container(cont_title)
			self.assertEqual(len(objects), 1)
		except swiftclient.ClientException:
			raise Exception("Access denied")
		else:
			#folder.delete_folder()
			print 'folder_id', cont_title
			self.assertNotEqual(Folder.objects.filter(pk=cont_title), None)

	def test_get_templ_url(self):
		file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dropbox/__init__.py')
		from mimetypes import MimeTypes
		mime = MimeTypes()
		mime_type = mime.guess_type(file_path)
		my_file = open(file_path, 'rb').read() ### need to read

		user = User.objects.get(id='1')
		folder = Folder.create_folder('test_folder', user)
		folder.upload_file(file_title='__init__.py',  file_contents=my_file, content_type=mime_type)

		url = folder.get_temp_download_urls(file_title='__init__.py')
		print 'url: '+str(url)
		cont_title = str(folder.id)
		try:
			conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL)
			_m, objects = conn.get_container(cont_title)
			self.assertEqual(len(objects), 1)
		except swiftclient.ClientException:
			raise Exception("Access denied")

		folder.delete_folder()   
		self.assertEqual(Folder.objects.filter(id=cont_title).count(), 0)


class Resources_Test_cases(ResourceTestCase):
	fixtures = ['app_data.json','user_data.json'] 
	def setUp(self):
		super(self.__class__, self).setUp()

		self.api_path_container= '/api/v1/storage/'
		
		self.get_resp_container = lambda path: self.api_client.get(
			self.api_path_container + path,
			format='json',           
			HTTP_HOST='localhost') 
		self.get_des_res = lambda path: self.deserialize(self.get_resp+container(path))


	def test_upload_download_file(self):
		user = User.objects.get(id='1')
		folder = Folder.create_folder(title='test_folder', user=user)
		cont_title = str(folder.id)
		try:
			conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL)
			_m, objects = conn.get_container(cont_title) 
			self.assertEqual(len(objects), 0)
		except swiftclient.ClientException:
			raise Exception("Access denied")
		else: 
			file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
								 'dropbox/models.py')

			from mimetypes import MimeTypes
			mime = MimeTypes()
			mime_type = mime.guess_type(file_path)
			file_contents = open(file_path, "rb").read()
			filename='models.py'

			import base64
			post_data={
				'filename': filename,
				'content_type': mime_type,
				'uploaded_file': base64.b64encode(file_contents)
				}

			resp = self.api_client.post(self.api_path_container+cont_title+"/upload/",
					format='json', data=post_data)
			des_resp = self.deserialize(resp)     
			#print des_resp

			conn = swiftclient.Connection(user=USERNAME, key=KEY, authurl=AUTH_URL)

			_m, objects = conn.get_container(cont_title)
			self.assertEqual(len(objects), 1)
			#folder.delete_folder()
"""
			resp = self.api_client.get(self.api_path_container+cont_title+'/'+filename+'/download/', format='json')
			print self.api_path_container+cont_title+'/'+filename+'/download/'
			des_resp = self.deserialize(resp)

			import requests
			request = requests.get(des_resp['temp_url'], stream=True)
			context = ""
			for chunk in request.iter_content():
				context += chunk
			self.assertTrue(len(context) != 0)
			folder.delete_folder()
			#self.assertEqual(Folder.objects.all().count(), 0)
"""


	




