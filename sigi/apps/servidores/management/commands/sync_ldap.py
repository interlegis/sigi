# coding: utf-8
import ldap
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from sigi.apps.servidores.models import Servidor
from sigi.settings import *


class Command(BaseCommand):
    help = u'Sincroniza Usuários e Servidores com o LDAP'

    def handle(self, *args, **options):
        self.sync_groups()
        self.sync_users()

    def get_ldap_groups(self):
        filter = "(&(objectclass=Group))"
        values = ['cn', ]
        l = ldap.initialize(AUTH_LDAP_SERVER_URI)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(AUTH_LDAP_BIND_DN.encode('utf-8'), AUTH_LDAP_BIND_PASSWORD)
        result_id = l.search(AUTH_LDAP_GROUP, ldap.SCOPE_SUBTREE, filter, values)
        result_type, result_data = l.result(result_id, 1)
        l.unbind()
        return result_data

    def get_ldap_users(self):
        filter = "(&(objectclass=user))"
        values = ['sAMAccountName', 'userPrincipalName', 'givenName', 'sn', 'cn']
        l = ldap.initialize(AUTH_LDAP_SERVER_URI)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(AUTH_LDAP_BIND_DN.encode('utf-8'), AUTH_LDAP_BIND_PASSWORD)
        result_id = l.search(AUTH_LDAP_USER.encode('utf-8'), ldap.SCOPE_SUBTREE, filter, values)
        result_type, result_data = l.result(result_id, 1)
        l.unbind()
        return result_data

    def sync_groups(self):
        ldap_groups = self.get_ldap_groups()
        for ldap_group in ldap_groups:
            try:
                group_name = ldap_group[1]['cn'][0]
            except:
                pass
            else:
                try:
                    group = Group.objects.get(name=group_name)
                except Group.DoesNotExist:
                    group = Group(name=group_name)
                    group.save()
                    print "Group '%s' created." % group_name
        print "Groups are synchronized."

    def sync_users(self):
        ldap_users = self.get_ldap_users()

        def get_ldap_property(ldap_user, property_name, default_value=None):
            value = ldap_user[1].get(property_name, None)
            return value[0].decode('utf8') if value else default_value

        for ldap_user in ldap_users:
            username = get_ldap_property(ldap_user, 'sAMAccountName')
            if username:
                email = get_ldap_property(ldap_user, 'userPrincipalName', '')
                first_name = get_ldap_property(ldap_user, 'givenName', username)
                last_name = get_ldap_property(ldap_user, 'sn', '')[:30]
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    try:
                        user = User.objects.get(email=email)
                        old_username = user.username
                        user.username = username
                        print "User with email '%s' had his/her username updated from [%s] to [%s]." % (
                            email, old_username, username)
                    except User.DoesNotExist:
                        user = User.objects.create_user(
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                        )
                        print "User '%s' created." % username

                if not user.first_name == first_name:
                    user.first_name = first_name
                    print "User '%s' first name updated." % username
                if not user.last_name == last_name:
                    user.last_name = last_name
                    print "User '%s' last name updated." % username
                if not user.email == email:
                    user.email = email
                    print "User '%s' email updated." % username

                nome_completo = get_ldap_property(ldap_user, 'cn', '')
                try:
                    servidor = user.servidor
                except Servidor.DoesNotExist:
                    try:
                        servidor = Servidor.objects.get(nome_completo=nome_completo)
                    except Servidor.DoesNotExist:
                        servidor = user.servidor_set.create(nome_completo=nome_completo)
                        print "Servidor '%s' created." % nome_completo
                else:
                    if not servidor.nome_completo == nome_completo:
                        servidor.nome_completo = nome_completo
                        print "Full name of Servidor '%s' updated." % nome_completo

                servidor.user = user
                servidor.save()
                user.save()
        print "Users are synchronized."
