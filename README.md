Taiga contrib AD auth
=======================

The Taiga plugin for Active Directory authentication

Installation
------------

### Taiga Back

In your Taiga back, first install `libkrb5-dev` with the following command:

```bash
  sudo apt-get install libkrb5-dev
```

Finally, modify your `settings/local.py` and include it on `INSTALLED_APPS` and add your
KERBEROS configuration:

```python
  INSTALLED_APPS += ['taiga_contrib_ad_auth']

	# Rules for kerberos configs and capitalization apply here.
  # Kerberos realm of AD domain.
  AD_REALM = 'MYDOMAIN.LOCAL'

	# Allowed domains
	AD_ALLOWED_DOMAINS = ['mydomain.local']
	AD_DEFAULT_DOMAIN = 'mydomain.local'

	# TODO: More here

```

### Taiga Front

Change in your `dist/js/conf.json` the `loginFormType` setting to `"ad"`:

```json
...
    "loginFormType": "ad",
...
```


### Credits:

Based on ldap code fom [enskylin](https://github.com/ensky/taiga-contrib-ldap-auth) and kerberos code from [dpasqualin](https://github.com/dpasqualin/taiga-contrib-kerberos-auth).