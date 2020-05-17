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
	
	
	#test item token generation
	def test_encode_item_token(self):
		item = Item(name='Test')
		db.session.add(item)
		db.session.commit()
		token = item.generate_item_token('Tester')
		self.assertTrue(isinstance(token,bytes))
		
	def test_decode_item_token(self):
		item = Item(name='Test')
		db.session.add(item)
		db.session.commit()
		token = item.generate_item_token('Tester')
		self.assertTrue(isinstance(token,bytes))
		self.assertFalse(Item.decode_item_token(token) == None,None)
		
if __name__ == "__main__":
	unittest.main()