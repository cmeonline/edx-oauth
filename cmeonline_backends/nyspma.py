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
    BASE_URL = settings.NYSPMA_BACKEND_BASE_URL
    AUTHORIZATION_URL = BASE_URL + settings.NYSPMA_BACKEND_AUTHORIZATION_URL
    ACCESS_TOKEN_URL = BASE_URL + settings.NYSPMA_BACKEND_ACCESS_TOKEN_URL
    USER_QUERY = BASE_URL + settings.NYSPMA_BACKEND_USER_QUERY
    SOCIAL_AUTH_SANITIZE_REDIRECTS = False
    REQUEST_TOKEN_METHOD = 'POST'
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('id', 'id')
    ]
    SCOPE_SEPARATOR = ' '
    DEFAULT_SCOPE = ['public', 'write']
    REDIRECT_STATE = False

    def __init__(self, *args, **kwargs):

        logger.debug('__init__. AUTHORIZATION_URL: {auth}, ACCESS_TOKEN_URL: {token}, USER_QUERY: {usr}'.format(
            auth = self.AUTHORIZATION_URL,
            token = self.ACCESS_TOKEN_URL,
            usr = self.USER_QUERY
        ))

        super(NYSPMAOAuth2, self).__init__(*args, **kwargs)

    @property
    def base_url(self):
        logger.debug('base_url() - entered.')
        return self.BASE_URL

    def urlopen(self, url):
        logger.debug('urlopen() - entered.')
        return urlopen(url).read().decode("utf-8")

    def get_key_and_secret(self):
        logger.debug('get_key_and_secret() - entered. Client_id: {}'.format(self.CLIENT_ID))
        return (self.CLIENT_ID, self.CLIENT_SECRET)

    def get_user_id(self, details, response):
        logger.debug('get_user_id() - details: {}'.format(details))
        logger.debug('get_user_id() - response: {}'.format(response))
        return details['username']

    def get_user_details(self, response):
        logger.debug('get_user_details() - entered. response: {}'.format(response))
        return {
                'username': str(response.get('id')),
                'email': response['email'],
                'fullname': response['first_name'] + ' ' + response['last_name'],
                'first_name': response['first_name'],
                'last_name': response['last_name'],
                }

    def user_data(self, access_token, *args, **kwargs):
        logger.debug('user_data() - entered.')
        logger.debug('user_data() - entered. args: {}'.format(args))
        logger.debug('user_data() - entered. kwargs: {}'.format(kwargs))
        response = self.get_json(self.USER_QUERY,
                                 params={'access_token': access_token})
        logger.debug('user_data() - user_query: {}'.format(response))

        response = {
            'email': response['email_address'],
            'name': response['first_name'],
            'fullname': response['first_name'] + ' ' +
                        response['last_name'],
            'first_name': response['first_name'],
            'last_name': response['last_name'],
            'user_id': str(response['id']),
        }
        logger.debug('get_user_details() - returning these results: {}'.format(response))
        return response
