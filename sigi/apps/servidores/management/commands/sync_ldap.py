# coding= utf-8
import ldap
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from sigi.settings import *
from sigi.apps.servidores.models import Servidor

class Command(BaseCommand):
    help = 'Sincroniza Usuários e Servidores com o LDAP'

    def handle(self, *args, **options):
        self.sync_groups()
        self.sync_users()

    def get_ldap_groups(self):
        filter = "(&(objectclass=Group))"
        values = ['cn',]
        l = ldap.initialize(AUTH_LDAP_SERVER_URI)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(AUTH_LDAP_BIND_DN.encode('utf-8'),AUTH_LDAP_BIND_PASSWORD)
        result_id = l.search(AUTH_LDAP_GROUP, ldap.SCOPE_SUBTREE, filter, values)
        result_type, result_data = l.result(result_id, 1)
        l.unbind()
        return result_data

    def get_ldap_users(self):
        filter = "(&(objectclass=user))"
        values = ['sAMAccountName', 'userPrincipalName', 'givenName', 'sn', 'cn' ]
        l = ldap.initialize(AUTH_LDAP_SERVER_URI)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(AUTH_LDAP_BIND_DN.encode('utf-8'),AUTH_LDAP_BIND_PASSWORD)
        result_id = l.search(AUTH_LDAP_USER.encode('utf-8'), ldap.SCOPE_SUBTREE, filter, values)
        result_type, result_data = l.result(result_id, 1)
        l.unbind()
        return result_data

    def sync_groups(self):
        ldap_groups = self.get_ldap_groups()
        for ldap_group in ldap_groups:
            try: group_name = ldap_group[1]['cn'][0]
            except: pass
            else:
                try: group = Group.objects.get(name=group_name)
                except Group.DoesNotExist:
                    group = Group(name=group_name)
                    group.save()
                    print "Group '%s' created." % group_name
        print "Groups are synchronized."

    def sync_users(self):
        ldap_users = self.get_ldap_users()
        for ldap_user in ldap_users:
            try: username = ldap_user[1]['sAMAccountName'][0]
            except: pass
            else:
                try: email = ldap_user[1]['userPrincipalName'][0]
                except: email = ''
                try: first_name = ldap_user[1]['givenName'][0]
                except: first_name = username
                try: last_name = ldap_user[1]['sn'][0][:30]
                except: last_name = ''
                try: user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = User.objects.create_user(username, email, username)
                    user.first_name = first_name
                    user.last_name = last_name
                    print "User '%s' created." % username
                try: nome_completo = ldap_user[1]['cn'][0]
                except: nome_completo = ''
                try: 
                    servidor = user.servidor
                    if not servidor.nome_completo == nome_completo.decode('utf8'):
                    	servidor.nome_completo = nome_completo
                        print "Servidor '%s' updated." % nome_completo
                except Servidor.DoesNotExist:
                    try: servidor = Servidor.objects.get(nome_completo=nome_completo)
                    except Servidor.DoesNotExist:
                        servidor = user.servidor_set.create(nome_completo=nome_completo)
                        print "Servidor '%s' created." % nome_completo
                    else:
                        if not user.email == email.decode('utf8'):
                            user.email = email
                            print "User '%s' email updated." % username
                        if not user.first_name == first_name.decode('utf8'):
                            user.first_name = first_name
                            print "User '%s' first name updated." % username
                        if not user.last_name == last_name.decode('utf8'):
                            user.last_name = last_name
                            print "User '%s' last name updated." % username
		servidor.user = user
                servidor.save()
                user.save()
        print "Users are synchronized."
