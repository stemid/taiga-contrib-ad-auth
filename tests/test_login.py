#!/usr/bin/env python

import sys
from configparser import RawConfigParser

# Locate taiga-back libs
sys.path.append('../taiga-back/')

from taiga_contrib_ad_auth import connector

conf_defaults = {
    'DEFAULT': {
        'username': 'user@mydomain.local',
        'password': 'secret.'
    }
}

config = RawConfigParser(defaults=conf_defaults)
config.readfp(open('tests/tests_local.cfg'))

def test_ad_login_success():
    (email, username) = connector.login(
        config.get('DEFAULT', 'username'),
        config.get('DEFAULT', 'password')
    )
