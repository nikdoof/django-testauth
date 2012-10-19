import django.utils.simplejson as json
import urllib
import urllib2
from hashlib import sha1
from django.conf import settings
from django.contrib.auth.models import User, Group


class TESTAuthBackend:
    """
    Django authentication backend for authenticating against TEST's Auth System.
    """
    def authenticate(self, username=None, password=None):

        if username and password:

            api_url = getattr(settings, 'TEST_AUTH_LOGIN_URL', 'https://auth.pleaseignore.com/api/1.0/login/')
            params = {'user': username, 'pass': sha1(password).hexdigest()}
            try:
                raw = urllib2.urlopen('%s?%s' % (api_url, urllib.urlencode(params)))
            except urllib2.HTTPError:
                return
            else:
                obj = json.loads(raw.read())
                if 'auth' in obj and obj['auth'] == 'ok':
                    user, created = User.objects.get_or_create(username=username.lower())
                    if created:
                        user.set_unusable_password()
                    if 'email' in obj and obj['email'] != '':
                        user.email = obj['email']
                    if 'primarycharacter' in obj and 'name' in obj['primarycharacter']:
                        user.first_name = obj['primarycharacter']['name']
                    user.save()

                    if getattr(settings, 'TEST_AUTH_CREATE_GROUPS', False):
                        user.groups.clear()
                        for g in obj['groups']:
                            group, created = Group.objects.get_or_create(name=g['name'])
                            user.groups.add(group)

                    return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return
