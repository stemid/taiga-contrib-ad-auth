Taiga contrib AD auth
=======================

The Taiga plugin for Active Directory authentication.

This is a combination of taiga-contrib-ldap-auth and taiga-contrib-kerberos-auth because I felt there was a need for an AD plugin that could authenticate using kerberos and fetch attributes using ldap.

So this plugin first and foremost authenticates using Kerberos, and if this auth fails the plugin also fails. 

At success the plugin attempts to fetch attributes from AD using ldap and the provided credentials that it used to authenticate with kerberos.

Installation
------------

### Taiga Back

In your Taiga back, first install `libkrb5-dev` with the following command:

```bash
  sudo apt-get install libkrb5-dev
```

Finally, modify your `settings/local.py` and include it on `INSTALLED_APPS` and add your AD configuration:

```python
  INSTALLED_APPS += ['taiga_contrib_ad_auth']

	# Active Directory configuration
	AD_REALM = 'MYDOMAIN.LOCAL'
	AD_ALLOWED_DOMAINS = ['mydomain.local']

	AD_LDAP_SERVER = 'ldaps://dc01.mydomain.local/'
	AD_LDAP_PORT = 636
	AD_SEARCH_BASE = 'ou=Company,dc=mydomain,dc=local'
	AD_EMAIL_PROPERTY = 'mail'
	#AD_SEARCH_FILTER = 
	#AD_BIND_DN =
	#AD_BIND_PASSWORD =
```

The options are described here, plus some additional options for advanced configs.

* `AD_REALM` is normally case sensitive when dealing with Kerberos.
* Using multiple domains in `AD_ALLOWED_DOMAINS` is as of yet untested.
* `AD_LDAP_SERVER` can be a single hostname, ip or an LDAP URI.
* `AD_EMAIL_PROPERTY`: `mail` is not present in every AD setup, for example an internal network might not have need of it so an alternative could be `userPrincipalName`.
* `AD_FULLNAME_PROPERTY` is by default `name`.
* `AD_BIND_DN` is left unset by default to use the kerberos credentials for LDAP binding.
* `AD_SEARCH_FILTER` is by default defined as `(&(objectClass=user)(sAMAccountName={username}))`.


### Taiga Front

Change in your `dist/js/conf.json` the `loginFormType` setting to `"ad"`:

```json
...
    "loginFormType": "ad",
...
```

### Credits

Based on ldap code fom [enskylin](https://github.com/ensky/taiga-contrib-ldap-auth) and kerberos code from [dpasqualin](https://github.com/dpasqualin/taiga-contrib-kerberos-auth).
