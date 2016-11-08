#!/usr/bin/env python
# I don't know how to use Mock or pytest so this is the best test I can think
# of. It works if you run it alongside a configured taiga-back install.

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


if __name__ == '__main__':
    test_ad_login_success()
