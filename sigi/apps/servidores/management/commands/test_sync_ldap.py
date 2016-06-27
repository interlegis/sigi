# -*- coding: utf-8 -*-
import pytest
from django.contrib.auth.models import User
from django_dynamic_fixture import G

from sigi.apps.servidores.management.commands.sync_ldap import Command

pytestmark = pytest.mark.django_db


class StubCommand(Command):

    def __init__(self, users):
        super(StubCommand, self).__init__()
        self.users = users

    def get_ldap_users(self):
        return self.users


def create_stub_user(username, nome_completo, first_name, last_name, email):
    user = G(User, username=username, first_name=first_name, last_name=last_name, email=email)
    user.servidor.nome_completo = nome_completo
    return user

ALEX_LDAP, BRUNO_LDAP, RITA_LDAP = [
    ('...',
        {'cn': ['Alex Lima'],
         'givenName': ['Alex'],
         'sAMAccountName': ['alexlima'],
         'sn': ['Lima'],
         'userPrincipalName': ['alexlima@interlegis.leg.br']}),

    ('...',
        {'cn': ['Bruno Almeida Prado'],
         'givenName': ['Bruno'],
         'sAMAccountName': ['bruno'],
         'sn': ['Almeida Prado'],
         'userPrincipalName': ['bruno@interlegis.leg.br']}),

    ('...',
        {'cn': ['Cl\xc3\xa1udia de C\xc3\xa1ssia'],
         'givenName': ['Cl\xc3\xa1udia'],
         'sAMAccountName': ['claudia'],
         'sn': ['de C\xc3\xa1ssia'],
         'userPrincipalName': ['claudia@interlegis.leg.br']}),
]


@pytest.mark.parametrize("before, ldap_users, after, messages", [
    # new user from ldap is created
    ([],
     [ALEX_LDAP],
     [(u'alexlima', u'Alex Lima', u'Alex', u'Lima', u'alexlima@interlegis.leg.br')],
     u'''
User 'alexlima' created.
Users are synchronized.
     '''),

    # nothing changes
    ([(u'alexlima', u'Alex Lima', u'Alex', u'Lima', u'alexlima@interlegis.leg.br')],
     [ALEX_LDAP],
     [(u'alexlima', u'Alex Lima', u'Alex', u'Lima', u'alexlima@interlegis.leg.br')],
     u'''
Users are synchronized.
     '''),

    # unicode encoding from LDAP data works well
    ([('claudia', u'Cláudia de Cássia', u'Cláudia', u'de Cássia', 'claudia@interlegis.leg.br', )],
     [RITA_LDAP],
     [(u'claudia', u'Cláudia de Cássia', u'Cláudia', u'de Cássia', u'claudia@interlegis.leg.br', )],
     u'''
Users are synchronized.
     '''),

    # update: full name, first name, last name, email
    ([('alexlima', '___', '___', '___', '___', ),
      ('bruno', 'Bruno Almeida Prado', '___', 'Almeida Prado', '___', ),
      ('claudia', '___', u'Cláudia', '___', 'claudia@interlegis.leg.br', )],
     [ALEX_LDAP, BRUNO_LDAP, RITA_LDAP],
     [(u'alexlima', u'Alex Lima', u'Alex', u'Lima', u'alexlima@interlegis.leg.br', ),
      (u'bruno', u'Bruno Almeida Prado', u'Bruno', u'Almeida Prado', u'bruno@interlegis.leg.br', ),
      (u'claudia', u'Cláudia de Cássia', u'Cláudia', u'de Cássia', u'claudia@interlegis.leg.br', )],
     u'''
User 'alexlima' first name updated.
User 'alexlima' last name updated.
User 'alexlima' email updated.
Full name of Servidor 'Alex Lima' updated.
User 'bruno' first name updated.
User 'bruno' email updated.
Full name of Servidor 'Bruno Almeida Prado' updated.
User 'claudia' last name updated.
Full name of Servidor 'Cláudia de Cássia' updated.
Users are synchronized.
      '''),

    # update username (username from LDAP not in base, so match user by email and update username)
    # TODO: is this functionality really necessary? If not remove this and corresponding code

    # connect servidor with nome_completo to user
    # TODO: is this functionality really necessary? If not remove this and corresponding code

    # create new servidor with nome_completo and connect to user
    # TODO: is this functionality really necessary? If not remove this and corresponding code


    # user not present in ldap is NOT deleted
    ([(u'alexlima', u'Alex Lima', u'Alex', u'Lima', u'alexlima@interlegis.leg.br', ),
      (u'bruno', u'Bruno Almeida Prado', u'Bruno', u'Almeida Prado', u'bruno@interlegis.leg.br', ),
      (u'claudia', u'Cláudia de Cássia', u'Cláudia', u'de Cássia', u'claudia@interlegis.leg.br', )],
     [ALEX_LDAP, RITA_LDAP],
     [(u'alexlima', u'Alex Lima', u'Alex', u'Lima', u'alexlima@interlegis.leg.br', ),
      (u'bruno', u'Bruno Almeida Prado', u'Bruno', u'Almeida Prado', u'bruno@interlegis.leg.br', ),
      (u'claudia', u'Cláudia de Cássia', u'Cláudia', u'de Cássia', u'claudia@interlegis.leg.br', )],
     u'''
Users are synchronized.
      '''),
])
def test_sync_users(before, ldap_users, after, messages, capsys):

    # setup
    for user_setup in before:
        if type(user_setup) == tuple:
            create_stub_user(*user_setup)
    assert User.objects.count() == len(before)

    command = StubCommand(ldap_users)
    command.sync_users()
    users = User.objects.all().order_by('username')
    for user, expected in zip(users, after):
        real = user.username, user.servidor.nome_completo, user.first_name, user.last_name, user.email
        assert real == expected

    # feedbak messages
    out, err = capsys.readouterr()
    assert out.strip() == messages.strip()
    assert err == ''
