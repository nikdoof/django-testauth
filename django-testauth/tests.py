import urllib
import BaseHTTPServer
from hashlib import sha1
from django.test import TestCase
from django.http import QueryDict
import django.utils.simplejson as json
from .auth import TESTAuthBackend


class DummyAuthAPIv1(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    This class represents a dummy Auth API v1.0 server used to test the API
    calls within the authentication plugin
    """

    # Test user/password combos for authentication
    users = {
        'invaliduser': sha1('invalidpassword').hexdigest(),
        'testuser': sha1('testtest').hexdigest(),
    }

    # Test data for authorization and details
    user_data = {
        'testuser': {'auth': 'ok', 'email': 'testmail@testing.com',
                     'primarycharacter': {'name': 'Test Char' },
                     'groups': [ {'name': 'G1'}, {'name': 'G2'} ],
                    }
    }

    def get_data(self, username):
        if username in self.user_data:
            return json.dumps(self.user_data[username])
        return json.dumps({})

    def test_login(self, username, password):
        if username in self.users and self.users[username] == password:
            return True
        return False

    def do_GET(self):
        path, query = urllib.unquote(self.path).split('?')

        # Cheat and use some Django classes to do the hard work for us
        qd = QueryDict(query_string=query)

        self.send_response(200)
        self.send_header("Content-Type", "text/json")
        if self.test_login(qd['user'], qd['pass']):
            self.wfile.write(self.get_data(qd['user']))
        else:
            self.wfile.write(json.dumps({'auth': 'failed'}))


class AuthLogin(TestCase):
    def setUp(self):
        self.auth = TESTAuthBackend()

    def testLogin(self):
        self.assertEquals(self.auth.authenticate(username='invaliduser', password='asdasd'), None)
        self.assertTrue(self.auth.authenticate(username='testuser', password='testtest'))
