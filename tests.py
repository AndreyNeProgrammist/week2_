import unittest
import requests

class TestEncryptionAPI(unittest.TestCase):

    def setUp(self):
        self.base_url = 'http://localhost:5000'
        # Setup any necessary test data or configurations

    def test_add_user(self):
        # Test adding a user
        data = {'login': 'testuser', 'secret': 'test123'}
        response = requests.post(f'{self.base_url}/users', json=data)
        self.assertEqual(response.status_code, 201)

    def test_get_users(self):
        # Test getting a list of users
        response = requests.get(f'{self.base_url}/users')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('users' in response.json())

    # Add more test cases for other API endpoints

    def tearDown(self):
        # Clean up any test data or states if needed
        pass

if __name__ == '__main__':
    unittest.main()

