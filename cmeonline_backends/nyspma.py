"""
Written by:     Lawrence McDaniel
                lpm0073@gmail.com
                lawrencemcdaniel.com

Date:           April 9, 2019

Usage:          A Python Social Auth backend that authenticates against
                NY State Podiatric Medical Association web site. Built for
                Open edX but can be used with any Identity Consumer client

                BaseOAuth2 provides most of the functionality needed to
                implement an oauth backend. This module primarily overrides
                some of the social_core module default values, plus, it
                implements a couple of methods that must be implements in the
                subclass:
                    get_user_details()
                    user_data()

NYSPMA contact information:
                admin team for https://associationdatabase.com
                David Zachrich dave@tcssoftware.com
                Tim Rorris tim@tcssoftware.com

Installation:   This modules assumes the existence of several python constants.
                1. For Open edX the following must be added to aws.py:
                NYSPMA_BACKEND_CLIENT_ID = ENV_TOKENS.get('NYSPMA_BACKEND_CLIENT_ID', None)
                NYSPMA_BACKEND_CLIENT_SECRET = ENV_TOKENS.get('NYSPMA_BACKEND_CLIENT_SECRET', None)

                * the production implementation adds default values based on whatever the client provided
                  leading up to deployment.

                2. each of these environment tokens must be added to lms.env.json


References:     https://python-social-auth-docs.readthedocs.io/en/latest/
                https://github.com/python-social-auth
                https://github.com/python-social-auth/social-core
                https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/configuration/tpa/
"""
import json
from urllib import urlencode
from urllib2 import urlopen
from social_core.backends.oauth import BaseOAuth2
from django.conf import settings

from logging import getLogger
logger = getLogger(__name__)


class NYSPMAOAuth2(BaseOAuth2):
    """
    NYSPMA OAuth authentication backend.
    """
    name = 'nyspma'             # to set the name that appears in the django admin
                                # drop-down box, "Backend name" in the
                                # "Add Provider Configuration (OAuth)" screen

    DEBUG_LOG = True            # true if you want to create a log trace of
                                # calls to this module.


    """
    don't change these.
    """
    ID_KEY = 'email_address'    # determines which json key
                                # contains the id value identifying
                                # the user on the identity provider server
    BASE_URL = 'https://associationdatabase.com'
    AUTHORIZATION_URL = BASE_URL + '/oauth/authorize'
    ACCESS_TOKEN_URL = BASE_URL + '/oauth/access_token'
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False

    """
    these are provided directly by TCS Software.
    """
    SCOPE_SEPARATOR = ' '
    DEFAULT_SCOPE = ['public', 'write']

    ## these i'm not entirely sure about. i believe that downstream consumers
    ## of the authentication response -- in the 3rd party auth pipeline -- might
    ## receive a parameter re "extra data" but as of yet i have not see any
    ## examples of how this works.
    EXTRA_DATA = [
        ('id', 'id'),
        ('org_id', 'org_id'),
        ('date_joined', 'date_joined')
    ]

    #def get_user_id(self, details, response):
    #    return response['id']

    #def get_username(self, strategy, details, backend, user=None, *args, **kwargs):
    #    return details['username']

    """
    i believe that this is the json object that gets consumed within consumers
    of the 3rd party pipeline. we want these keys to match up with whatever
    Open edX is expecting.

    more details: https://github.com/edx/edx-platform/tree/master/common/djangoapps/third_party_auth
    """
    def get_user_details(self, response):
        """Return user details from NYSPMA account"""
        if self.DEBUG_LOG:
            logger.info('get_user_details() - response: {}'.format(response))

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

    """
    this will return a json object that exactly matches whatever the
    identify provider sends.
    """
    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        if self.DEBUG_LOG:
            logger.info('user_data() - entered')

        url = self.user_query() + urlencode({
            'access_token': access_token
        })
        try:
            return json.loads(self.urlopen(url))
        except ValueError:
            return None

    def get_key_and_secret(self):
        if self.DEBUG_LOG:
            logger.info('get_key_and_secret() - client_id: {}'.format(settings.NYSPMA_BACKEND_CLIENT_ID))

        return (settings.NYSPMA_BACKEND_CLIENT_ID, settings.NYSPMA_BACKEND_CLIENT_SECRET)
