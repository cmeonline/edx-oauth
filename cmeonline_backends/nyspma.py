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
logger.info('backends.nyspma.py - instantiated')

class NYSPMAOAuth2(BaseOAuth2):
    """NYSPMA OAuth authentication backend"""
    name = 'nyspma'

    CLIENT_ID = settings.NYSPMA_BACKEND_CLIENT_ID
    CLIENT_SECRET = settings.NYSPMA_BACKEND_CLIENT_SECRET
    AUTHORIZATION_URL = 'https://staging.associationdatabase.com' + settings.NYSPMA_BACKEND_AUTHORIZATION_URL
    ACCESS_TOKEN_URL = 'https://staging.associationdatabase.com' + settings.NYSPMA_BACKEND_ACCESS_TOKEN_URL
    USER_QUERY = 'https://staging.associationdatabase.com' + settings.NYSPMA_BACKEND_USER_QUERY

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

        logger.info('__init__. AUTHORIZATION_URL: {auth}, ACCESS_TOKEN_URL: {token}, USER_QUERY: {usr}'.format(
            auth = self.AUTHORIZATION_URL,
            token = self.ACCESS_TOKEN_URL,
            usr = self.USER_QUERY
        ))

        super(NYSPMAOAuth2, self).__init__(*args, **kwargs)

    @property
    def base_url(self):
        logger.info('base_url() - entered.')
        # env = self.setting('ENVIRONMENT', default='staging')
        env = 'staging'

        if env == 'staging':
            return 'https://staging.associationdatabase.com'
        elif env == 'production':
            return 'https://associationdatabase.com'

        raise AuthException(
            'Invalid environment was found `{env}`, '
            'valid choices are `production` and `staging`.'.format(
                env=env,
            ))

    def urlopen(self, url):
        logger.info('urlopen() - entered.')
        return urlopen(url).read().decode("utf-8")

    def get_key_and_secret(self):
        logger.info('get_key_and_secret() - entered. Client_id: {}'.format(self.CLIENT_ID))
        return (self.CLIENT_ID, self.CLIENT_SECRET)

    def get_user_id(self, details, response):
        logger.info('get_user_id() - details: {}'.format(details))
        logger.info('get_user_id() - response: {}'.format(response))
        return details['username']

    def get_user_details(self, response):
        logger.info('get_user_details() - entered. response: {}'.format(response))
        """
        {
        "first_name":"System",
        "last_name":"Administrator",
        "prefix":"","suffix":"",
        "nickname":"System",
        "address_type":"Company",
        "address1":"425 Metro Place N #400",
        "address2":"",
        "city":"Dublin","state":"OH",
        "zip":"43017",
        "country":"",
        "phone":"(614) 451-5010",
        "fax":"","mobile":"",
        "date_joined":"",
        "exp_date":"",
        "category":"Administrator",
        "sub_category1":"",
        "email_address":"NYSPMAAdmin@TCSSoftware.com",
        "contact_no":0,
        "id":1174494,
        "org_id":"NYSPMA",
        "org_name":"TCS Software TESTING",
        "key_contact":false,
        "fp_timestamp":1554744745,
        "fingerprint":"99555eed098c74ee110514043bb2fe3d"
        }

        """
        return {
                'username': str(response.get('id')),
                'email': response['email_address'],
                'fullname': response['first_name'] + ' ' + response['last_name'],
                'first_name': response['first_name'],
                'last_name': response['last_name'],
                }

    def user_data(self, access_token, *args, **kwargs):
        logger.info('user_data() - entered.')
        logger.info('user_data() - entered. args: {}'.format(args))
        logger.info('user_data() - entered. kwargs: {}'.format(kwargs))
        """
        {u'last_name': u'Admin', u'suffix': u'', u'fp_timestamp': 1554917894, u'prefix': u'', u'exp_date': u'12/31/2050', u'email_address': u'nyspma_oauth_admin@nyspma.org', u'id': 2035093, u'date_joined': u'', u'category': u'Administrator', u'city': u'New York', u'first_name': u'OAuth2', u'zip': u'10018', u'state': u'NE', u'address_type': u'Company', u'org_name': u'NYSPMA', u'fax': u'', u'address1': u'555 Eighth Avenue', u'address2': u'Suite 1902', u'contact_no': 200179, u'phone': u'(646) 386-2528', u'fingerprint': u'62cbdf8f02d495e06d388786de49c41c', u'nickname': u'OAuth2', u'key_contact': False, u'sub_category1': u'', u'mobile': u'', u'country': u'', u'org_id': u'NYSPMA'}
        """
        response = self.get_json(self.USER_QUERY,
                                 params={'access_token': access_token})

        logger.info('user_data() - user_query: {}'.format(response))
        response = {
            'email': response['email_address'],
            'name': response['first_name'],
            'fullname': response['first_name'] + ' ' +
                        response['last_name'],
            'first_name': response['first_name'],
            'last_name': response['last_name'],
            'user_id': str(response['uid']),
        }
        logger.warning('get_user_details() - returning these results: {}'.format(response))
        return response
