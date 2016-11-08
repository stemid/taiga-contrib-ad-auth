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

from django.db import transaction as tx
from django.apps import apps

from taiga.base.utils.slug import slugify_uniquely
from taiga.auth.signals import user_registered as user_registered_signal
from taiga.auth.services import make_auth_response_data

from . import connector


@tx.atomic
def ad_register(username: str, email: str, full_name: str):
    """
    Register a new user from AD

    This can raise `exc.IntegrityError` exceptions in
    case of conflict found.

    :returns: User
    """
    user_model = apps.get_model("users", "User")

    try:
        # AD user association exist?
        user = user_model.objects.get(username=username)
    except user_model.DoesNotExist:
        # Create a new user
        username_unique = slugify_uniquely(
            username,
            user_model,
            slugfield="username"
        )
        user = user_model.objects.create(
            email=email,
            username=username_unique,
            full_name=full_name
        )
        user_registered_signal.send(sender=user.__class__, user=user)

    return user


def ad_login_func(request):
    username = request.DATA.get('username', None)
    password = request.DATA.get('password', None)

    email, full_name = connector.login(email=username, password=password)
    user = ad_register(username=username, email=email, full_name=full_name)
    data = make_auth_response_data(user)
    return data
