from auth import DredditAuthBackend
import unittest

class AuthLogin(unittest.TestCase):
    def setUp(self):
        self.auth = DredditAuthBackend()

    def testLogin(self):    
        self.assertEquals(self.auth.authenticate(username='invaliduser', password='asdasd'), None)
        self.assertTrue(self.auth.authenticate(username='testuser', password='testtest'))
