import unittest
import os
		
class TestAppSettings(unittest.TestCase):
	
	def test_app_name(self):
		message = "FLASK_APP environment variable has to be set to rest.py"
		self.assertEqual(os.environ.get('FLASK_APP'), 'pest.py', message)
		
class TestAppConfig(unittest.TestCase):

	def test_config(self):
		pass
	

if __name__=='__main__':
	unittest.main()