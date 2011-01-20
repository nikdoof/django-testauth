import hashlib
from string import lower
import django.utils.simplejson as json
import urllib
import urllib2
from hashlib import sha1
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
            api_url = 'https://auth.dredd.it/api/login/'
            params = { 'user': username, 'pass': sha1(password).hexdigest() }
            try:
                raw = urllib2.urlopen('%s?%s' % (api_url, urllib.urlencode(params)))
            except urllib2.HTTPError:
                pass
            else:
                obj = json.loads(raw.read())

                if 'auth' in obj and obj['auth'] == 'ok':
                    email = obj['email']
                    groups = obj['groups']
                    valid = True

        if valid:
            user, created = User.objects.get_or_create(username=username.lower())
            if created:
                user.set_unusable_password() # disable login through Model backend
                user.save()
            if email:
                user.email = email

            if hasattr(settings, 'DREDDIT_AUTH_CREATE_GROUPS') and settings.DREDDIT_AUTH_CREATE_GROUPS:
                for g in groups:
                    group, created = Group.objects.get_or_create(name=g['name'])
                    user.groups.add(group)

            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

