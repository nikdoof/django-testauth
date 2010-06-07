import hashlib
from string import lower
import simplejson as json
from django.contrib.auth.models import User, check_password
import settings

class DredditAuthBackend:
    """
    Django authentication backend for authenticating against Dreddit's Auth System.
    """
    def authenticate(self, username=None, password=None):

        valid = False

        if username and password:
            # Call the webservice
            api_url = 'https://auth.dredd.it/api/user/'
            import urllib
            import urllib2

            params = { 'user': username }
            raw = urllib2.urlopen('%s?%s' % (api_url, urllib.urlencode(params)))

            obj = json.loads(raw.read())

            if 'password' in obj and check_password(password, obj['password']):
                email = obj['email']
                valid = True

        if valid:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_unusable_password() # disable login through Model backend
                user.save()
            if not email is None:
                user.email = email
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

