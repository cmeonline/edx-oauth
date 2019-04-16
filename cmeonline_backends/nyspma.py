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
    reference docs for these settings:
    https://python-social-auth-docs.readthedocs.io/en/latest/configuration/settings.html
    """
    ID_KEY = 'email_address'    # determines which json key
                                # contains the id value identifying
                                # the user on the identity provider server
    BASE_URL = 'https://associationdatabase.com'
    LOGIN_URL = BASE_URL + '/aws/NYSPMA/login/login'
    AUTHORIZATION_URL = BASE_URL + '/oauth/authorize'
    ACCESS_TOKEN_URL = BASE_URL + '/oauth/token'
    USER_QUERY = '/api/user?'

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

    def get_user_id(self, details, response):
        if self.DEBUG_LOG:
            logger.info('get_user_id() - response: {}'.format(details))
        return details['username']

    def get_username(self, strategy, details, backend, user=None, *args, **kwargs):
        if self.DEBUG_LOG:
            logger.info('get_username() - details: {}'.format(details))
        return details['username']

    def login_url(self):
        url = self.LOGIN_URL
        if self.DEBUG_LOG:
            logger.info('login_url(): {}'.format(url))
        return url

    def authorization_url(self):
        url = self.AUTHORIZATION_URL
        if self.DEBUG_LOG:
            logger.info('authorization_url(): {}'.format(url))
        return url

    def access_token_url(self):
        url = self.ACCESS_TOKEN_URL
        if self.DEBUG_LOG:
            logger.info('access_token_url(): {}'.format(url))
        return url

    def user_query(self):
        url = self.USER_QUERY
        if self.DEBUG_LOG:
            logger.info('user_query(): {}'.format(url))
        return url

    def urlopen(self, url):
        if self.DEBUG_LOG:
            logger.info('urlopen() - url: {}'.format(url))
        return urlopen(url).read().decode("utf-8")


    """
    i believe that this is the json object that gets consumed within consumers
    of the 3rd party pipeline. we want these keys to match up with whatever
    Open edX is expecting.

    more details: https://github.com/edx/edx-platform/tree/master/common/djangoapps/third_party_auth
    """


    def get_key_and_secret(self):
        if self.DEBUG_LOG:
            logger.info('get_key_and_secret() - client_id: {}'.format(settings.NYSPMA_BACKEND_CLIENT_ID))

        return (settings.NYSPMA_BACKEND_CLIENT_ID, settings.NYSPMA_BACKEND_CLIENT_SECRET)
