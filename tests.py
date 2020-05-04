import os
import unittest
import json

from app import api, db
from app.models import User, Item

basedir = os.path.abspath(os.path.dirname(__file__))

class BasicTests(unittest.TestCase):
	
	#setup
	
	#executed prior to each test
	def setUp(self):
		api.config['TESTING'] = True
		api.config['WTF_SCRF_ENABLED'] = False
		api.config['DEBUG'] = False
		api.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		self.app = api.test_client()
		db.drop_all()
		db.create_all()
		
		self.assertEqual(api.debug,False)
		
	#executed after each test
	def tearDown(self):
		pass
	
	#helper method to register
	def register(self,login,password):
		return self.app.post(
			'/registration',
			json=dict(login=login,password=password)
			)
			
	#helper method to login
	def login(self,login,password):
		return self.app.post(
			'/login',
			json=dict(login=login,password=password)
		)
		
	#helper method to create item
	def send_item(self,auth_token,recipient_login,item_id):
		return self.app.post(
			'/send',
			json=dict(token=auth_token,login=recipient_login,id=item_id)
		)
		
	#helper function to get item
	def get_item(self,item_token,item_id):
		return self.app.get(
			'/get',
			json=dict(token=item_token,id=item_id)
		)
	
	#there's no index page, test for 404
	def test_index_page(self):
		response = self.app.get('/')
		self.assertEqual(response.status_code, 404)
		
	#test user registration
	def test_valid_user_registration(self):
		response = self.register('testman','tt12tt34')
		self.assertEqual(response.status_code,201)
		self.assertIn(b"User testman created!",response.data)
	
	#test with missing login
	def test_registration_missing_login(self):
		response = self.app.post(
			'/registration',
			json=dict(password='tt12tt34')
			)
		self.assertEqual(response.status_code, 400)
		
	#test send if the sent item gets received
	def test_send_get_item(self):
		#create 2 user
		sender = User(login='Sender',password='123')
		db.session.add(sender)
		recipient = User(login='Recipient',password='123')
		db.session.add(recipient)
		#create an item that user owns
		item = Item(name='Pen',owner=sender)
		db.session.add(item)
		db.session.commit()
		#assert that owner of the item is sender
		self.assertIs(sender,item.owner)
		#login user
		response = self.login('Sender','123')
		self.assertEqual(response.status_code,200)
		response = json.loads(response.data)
		#check if there's token
		self.assertIn('token',response)
		auth_token = response['token']
		#send item 
		response = self.send_item(auth_token,'Recipient','1')
		self.assertEqual(response.status_code,200)
		response = json.loads(response.data)
		#check if there's token
		self.assertIn('token',response)
		item_token = response['token']
		#get item
		response = self.get_item(item_token,'1')
		self.assertEqual(response.status_code,200)
		#check that recipient is now owner of the item
		item = Item.query.get(1)
		self.assertIsNotNone(item)
		recipient = User.query.filter_by(login='Recipient').first()
		self.assertIsNotNone(recipient)
		self.assertIs(recipient,item.owner)
		
if __name__ == "__main__":
	unittest.main()