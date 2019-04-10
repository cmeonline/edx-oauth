"""
Written by:     Lawrence McDaniel
                lpm0073@gmail.com
                lawrencemcdaniel.com

Date:           April 9, 2019
"""
import json
from urllib import urlencode
from urllib2 import urlopen
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import AuthException
from django.conf import settings

from logging import getLogger
logger = getLogger(__name__)
logger.debug('backends.nyspma.py - instantiated')

class NYSPMAOAuth2(BaseOAuth2):
    """NYSPMA OAuth authentication backend"""
    name = 'nyspma'

    CLIENT_ID = settings.NYSPMA_BACKEND_CLIENT_ID
    CLIENT_SECRET = settings.NYSPMA_BACKEND_CLIENT_SECRET
    #BASE_URL = settings.NYSPMA_BACKEND_BASE_URL
    #AUTHORIZATION_URL = settings.NYSPMA_BACKEND_AUTHORIZATION_URL
    #ACCESS_TOKEN_URL = settings.NYSPMA_BACKEND_ACCESS_TOKEN_URL
    #USER_QUERY = settings.NYSPMA_BACKEND_USER_QUERY
    SOCIAL_AUTH_SANITIZE_REDIRECTS = False
    REQUEST_TOKEN_METHOD = 'POST'
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('id', 'id'),
        ('org_id', 'org_id'),
        ('date_joined', 'date_joined')
    ]
    SCOPE_SEPARATOR = ' '
    DEFAULT_SCOPE = ['public', 'write']
    REDIRECT_STATE = False

    def __init__(self, *args, **kwargs):

        logger.debug('__init__. AUTHORIZATION_URL: {auth}, ACCESS_TOKEN_URL: {token}, USER_QUERY: {usr}'.format(
            auth = self.authorization_url(),
            token = self.access_token_url(),
            usr = self.user_query()
        ))

        super(NYSPMAOAuth2, self).__init__(*args, **kwargs)

    @property
    def base_url(self):
        return settings.NYSPMA_BACKEND_BASE_URL

    def authorization_url(self):
        return self.base_url() + settings.NYSPMA_BACKEND_AUTHORIZATION_URL

    def access_token_url(self):
        return self.base_url() + settings.NYSPMA_BACKEND_ACCESS_TOKEN_URL

    def user_query(self):
        return self.base_url() + settings.NYSPMA_BACKEND_USER_QUERY

    def urlopen(self, url):
        return urlopen(url).read().decode("utf-8")

    def get_key_and_secret(self):
        return (self.CLIENT_ID, self.CLIENT_SECRET)

    def get_user_id(self, details, response):
        return response['id']

    def get_username(self, strategy, details, backend, user=None, *args, **kwargs):
        return details['username']

    def get_user_details(self, response):
        """Return user details from NYSPMA account"""
        fullname, first_name, last_name = self.get_user_names(
            response.get('first_name', '') + ' ' + response.get('last_name', ''),
            response.get('first_name', ''),
            response.get('last_name', '')
        )
        return {'username': response.get('email_address', response.get('id')),
                'email': response.get('email_address', ''),
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name}

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = self.USER_QUERY + urlencode({
            'access_token': access_token
        })
        try:
            return json.loads(self.urlopen(url))
        except ValueError:
            return None
