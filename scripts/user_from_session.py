from django.contrib.auth.models import User
from django.contrib.sessions.models import Session


def user_from_session(session_key):
    session = Session.objects.get(session_key=session_key)
    uid = session.get_decoded().get('_auth_user_id')
    user = User.objects.get(pk=uid)
    print user.username, user.get_full_name(), user.email
    return user
