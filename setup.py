#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

setup(
    name = 'taiga-contrib-ad-auth',
    version = ":versiontools:taiga_contrib_ad_auth:",
    description = "The Taiga plugin for AD login",
    long_description = "",
    keywords = 'taiga, ad, kerberos, auth, plugin',
    author = 'stemid',
    author_email = 'swehack@gmail.com',
    url = 'https://github.com/stemid/taiga-contrib-ad-auth',
    license = 'AGPL',
    include_package_data = True,
    packages = find_packages(),
    install_requires=[
        'django >= 1.7',
        'kerberos >= 1.2.5',
        'ldap3 >= 2.1.0'
    ],
    setup_requires = [
        'versiontools >= 1.8',
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
