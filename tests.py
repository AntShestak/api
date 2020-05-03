import unittest
import os
		
class TestAppConfig(unittest.TestCase):
	
	def test_app_name(self):
		message = "FLASK_APP environment variable has to be set to app.py"
		self.assertEqual(os.environ.get('FLASK_APP'), 'app.py', message)
		

	

if __name__=='__main__':
	unittest.main()