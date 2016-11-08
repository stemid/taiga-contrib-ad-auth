# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from kerberos import checkPassword, BasicAuthError
from ldap3 import Server, Connection
from ldap3 import SIMPLE, SYNC, ASYNC, SUBTREE, NONE

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from taiga.base.connectors.exceptions import ConnectorBaseException


# Placeholders to allow for catching of errors from different parts of this
# plugin.
class KerberosLoginError(ConnectorBaseException):
    pass

class ADLoginError(ConnectorBaseException):
    pass

class LDAPLookupError(ConnectorBaseException):
    pass


# Kerberos
AD_REALM = getattr(settings, "AD_REALM", "")
AD_SHORT_REALM = getattr(
    settings,
    "AD_SHORT_REALM",
    AD_REALM.split('.')[0]
)
AD_ALLOWED_DOMAINS = getattr(settings, "AD_ALLOWED_DOMAINS", [])
AD_DEFAULT_DOMAIN = getattr(settings, "AD_DEFAULT_DOMAIN", AD_REALM)

# LDAP
AD_LDAP_SERVER = getattr(settings, "AD_LDAP_SERVER", "")
AD_LDAP_PORT = getattr(settings, "AD_LDAP_PORT", 0)
AD_USE_SSL = getattr(settings, "AD_USE_SSL", False)
AD_SEARCH_BASE = getattr(settings, "AD_SEARCH_BASE", "")
AD_SEARCH_FILTER = getattr(
    settings,
    "AD_SEARCH_FILTER",
    "(&(objectClass=user)(sAMAccountName={username}))"
)
AD_BIND_DN = getattr(settings, "AD_BIND_DN", None)
AD_BIND_PASSWORD = getattr(settings, "AD_BIND_PASSWORD", None)
AD_EMAIL_PROPERTY = getattr(settings, "AD_EMAIL_PROPERTY", "mail")
AD_FULLNAME_PROPERTY = getattr(settings, "AD_FULLNAME_PROPERTY", "name")


def do_ldap_search(username: str, password: str) -> tuple:
    """
    Searches the AD using the provided credentials from kerberos login and
    returns fullname and email address.
    """

    use_ssl = False
    if AD_LDAP_SERVER.lower().startswith('ldaps://') or AD_USE_SSL:
        use_ssl = True

    try:
        server = Server(
            AD_LDAP_SERVER,
            port=int(AD_LDAP_PORT),
            get_info=NONE,
            use_ssl=use_ssl
        )
    except Exception as e:
        raise ADLoginError({'error_message': str(e)})

    conn = None
    ldap_auth = SIMPLE
    ldap_user = '{realm}\{username}'.format(
        realm=AD_SHORT_REALM,
        username=username
    )
    ldap_password = password
    
    # By default we assume to use the kerberos credentials to bind, but it
    # is possible to use a pre-defined DN.
    if AD_BIND_DN is not None:
        ldap_user = AD_BIND_DN
        ldap_password = AD_BIND_PASSWORD

    try:
        conn = Connection(
            server,
            auto_bind=True,
            client_strategy=SYNC,
            user=ldap_user,
            password=ldap_password,
            authentication=ldap_auth,
            check_names=True
        )
    except Exception as e:
        raise ADLoginError({'error_message': str(e)})

    search_filter = AD_SEARCH_FILTER.format(
        username=username
    )

    try:
        conn.search(
            search_base=AD_SEARCH_BASE,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=[AD_EMAIL_PROPERTY, AD_FULLNAME_PROPERTY],
            paged_size=5
        )
    except Exception as e:
        raise LDAPLookupError({'error_message': str(e)})

    if len(conn.response):
        email = conn.response[0].get('raw_attributes').get(
            AD_EMAIL_PROPERTY
        )[0].decode('utf-8')
        fullname = conn.response[0].get('raw_attributes').get(
            AD_FULLNAME_PROPERTY
        )[0].decode('utf-8')

        return (email, fullname)


def login(email: str, password: str) -> tuple:
    
    allowed_domains = AD_ALLOWED_DOMAINS + [AD_REALM]

    validate_email = EmailValidator(whitelist=allowed_domains)

    if '@' in email:
        try:
            validate_email(email)
        except ValidationError as e:
            raise ADLoginError({'error_message': str(e)})

        username, domain = email.split('@')
    else:
        # If no @ used then try to use AD_DEFAULT_DOMAIN
        username, domain = email, AD_DEFAULT_DOMAIN
        email = '{username}@{domain}'.format(
            username=username,
            domain=domain
        )

    if domain not in allowed_domains:
        raise ADLoginError({'error_message': 'Invalid domain in e-mail'})

    try:
        checkPassword(username, password, "", AD_REALM)
    except BasicAuthError as e:
        errmsg, _junk = e.args
        if errmsg == "Cannot contact any KDC for requested realm":
            errmsg = "Error connecting to KERBEROS server"
            raise KerberosLoginError({"error_message": errmsg})
        elif errmsg == "Decrypt integrity check failed":
            errmsg = "KERBEROS account or password incorrect"
            raise KerberosLoginError({"error_message": errmsg})
        else:
            raise KerberosLoginError({"error_message": errmsg})
    except Exception as e:
        raise ADLoginError({'error_message': str(e)})

    # Lookup email and username from AD
    (ldap_email, ldap_fullname) = None, None
    try:
        ldap_email, ldap_fullname = do_ldap_search(username, password)
    except Exception as e:
        pass

    # Return a fullname property if available from LDAP query.
    if ldap_fullname:
        username = ldap_fullname

    if ldap_email:
        email = ldap_email

    return (email, username)

