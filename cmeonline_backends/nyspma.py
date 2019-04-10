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
    AUTHORIZATION_URL = ''
    ACCESS_TOKEN_URL = ''
    USER_QUERY = ''

    SOCIAL_AUTH_SANITIZE_REDIRECTS = False

    REQUEST_TOKEN_METHOD = 'POST'
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('id', 'id')
    ]
    SCOPE_SEPARATOR = ','
    DEFAULT_SCOPE = ['basic']
    REDIRECT_STATE = False

    def __init__(self, *args, **kwargs):
        AUTHORIZATION_URL = 'https://staging.associationdatabase.com' + settings.NYSPMA_BACKEND_AUTHORIZATION_URL
        ACCESS_TOKEN_URL = 'https://staging.associationdatabase.com' + settings.NYSPMA_BACKEND_ACCESS_TOKEN_URL
        USER_QUERY = 'https://staging.associationdatabase.com' + settings.NYSPMA_BACKEND_USER_QUERY

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
        logger.info('get_key_and_secret() - entered.')
        return (self.CLIENT_ID, self.CLIENT_SECRET)

    def get_user_id(self, details, response):
        logger.info('get_user_id() - details: {}'.format(details))
        logger.info('get_user_id() - response: {}'.format(response))
        return details['username']

    def get_user_details(self, response):
        logger.info('get_user_details() - entered. response: {}'.format(response))
        """
        {
        "provider": "tcs",
        "uid": 1174494,
        "info": {
                "first_name":"System",
                "last_name":"Administrator",
                "prefix":"","suffix":"",
                "nickname":"System",
                "address_type":"Company",
                "address1":"425 Metro Place N #400",
                "address2":"","city":"Dublin",
                "state":"OH",
                "zip":"43017",
                "country":"",
                "phone":"(614) 451-5010",
                "fax":"",
                "mobile":"",
                "date_joined":"",
                "exp_date":"",
                "category":"Administrator",
                "sub_category1":"",
                "email_address":"NYSPMAAdmin@TCSSoftware.com",
                "contact_no":0,"id":1174494,
                "org_id":"NYSPMA",
                "org_name":"TCS Software TESTING",
                "key_contact":false,
                "fp_timestamp":1554740628,
                "fingerprint":"f248afeae3ebd8c68a71762b9224e4ef",
                "token":"a18087a473448827f5b7ce481fd687c2d80f056e07537beff9249cc83d868f40"
        },
        "credentials":  {
                        "token":"a18087a473448827f5b7ce481fd687c2d80f056e07537beff9249cc83d868f40",
                        "refresh_token":"306c96e8747936e9f313ed0ca61ca5eb5928dc5bb369d1a460df788b6154f8af",
                        "expires_at":1554747826,
                        "expires":true
                        },
        "extra":        {}
        }
        """
        return {
                'username': str(response.get('uid')),
                'email': response['info']['email_address'],
                'fullname': response['info']['first_name'] + ' ' + response['info']['last_name'],
                'first_name': response['info']['first_name'],
                'last_name': response['info']['last_name'],
                }

    def user_data(self, access_token, *args, **kwargs):
        logger.info('user_data() - entered.')
        logger.info('user_data() - entered. args: {}'.format(args))
        logger.info('user_data() - entered. kwargs: {}'.format(kwargs))
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
        logger.info('get_user_details() - entered.')
        response = self.get_json(self.USER_QUERY,
                                 params={'access_token': access_token})
        response = {
            'email': response['email_address'],
            'name': response['first_name'],
            'fullname': response['first_name'] + ' ' +
                        response['last_name'],
            'first_name': response['first_name'],
            'last_name': response['last_name'],
            'user_id': str(response['id']),
        }
        logger.warning('get_user_details() - returning these results: {}'.format(response))
        return response
