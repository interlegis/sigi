# Generated by Django 4.2.4 on 2023-10-10 11:26

import ldap
from django.db import migrations
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model
from django_auth_ldap.config import _DeepStringCoder
from sigi.apps.utils import to_ascii
from sigi.apps.servidores.models import Servidor
from sigi.apps.servidores.utils import (
    mescla_users,
    mescla_servidores,
    servidor_update_from_ldap,
    user_staff_and_group,
)


def update_user_from_ldap(user, ldap_attrs):
    for user_attr, ldap_attr in settings.AUTH_LDAP_USER_ATTR_MAP.items():
        setattr(user, user_attr, ldap_attrs.get(ldap_attr, [""])[0])
    user.username = ldap_attrs.get("sAMAccountName", [""])[0]
    user_staff_and_group(user, ldap_attrs)


def forwards(apps, schema_editor):
    if not hasattr(settings, "AUTH_LDAP_SERVER_URI"):
        # Não está conectado ao LDAP. Nada a fazer
        return

    User = get_user_model()

    coder = _DeepStringCoder("utf8")
    connect = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    connect.protocol_version = 3
    connect.set_option(ldap.OPT_REFERRALS, 0)
    connect.simple_bind_s(
        settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD
    )

    # Eliminar usuário "administrador", transferindo seu log para usuário
    # "interlegis".

    if (
        User.objects.filter(
            username__in=["administrador", "interlegis"]
        ).count()
        == 2
    ):
        user = User.objects.get(username="administrador")
        user_target = User.objects.get(username="interlegis")
        user.logentry_set.update(user=user_target)
        user.delete()
        print(
            f"\n\tUser {user.username} deleted. Logs to {user_target.username}"
        )

    # Unificar usuários com nomes iguais minusculos > MAIÚSCULOS

    print("\tJoin users with same usernames in upper/lower cases...")

    joined_names = set()

    for user in User.objects.all():
        if (
            user.username.upper() not in joined_names
            and User.objects.filter(username__iexact=user.username)
            .exclude(id=user.id)
            .exists()
        ):
            user_source = User.objects.get(username=user.username.lower())
            user_target = User.objects.get(username=user.username.upper())
            print(f"\t\t{user_source.username} > {user_target.username}")
            mescla_users(user_source, user_target)
            joined_names.add(user.username.upper())

    # Identificar e atualizar todos os users que existem no LDAP #

    valid_users = dict()
    for user in User.objects.all():
        rdata = connect.search_s(
            settings.AUTH_LDAP_USER,
            ldap.SCOPE_SUBTREE,
            ldap.filter.filter_format("(sAMAccountName=%s)", [user.username]),
        )
        if rdata:
            dn, ldap_attrs = coder.decode(rdata[0])
            valid_users[dn] = user
            update_user_from_ldap(user, ldap_attrs)
            if user.servidor:
                servidor_update_from_ldap(user.servidor, ldap_attrs)

    # Identifica servidores que estão no LDAP mas, por algum motivo, não estão
    # vinculados a algum 'valid_user' identificado ali acima

    for servidor in Servidor.objects.exclude(
        user__in=valid_users.values()
    ).exclude(externo=True):
        ldap_filter = ldap.filter.filter_format(
            "(cn=%s)", [servidor.nome_completo]
        )
        rdata = connect.search_s(
            settings.AUTH_LDAP_USER, ldap.SCOPE_SUBTREE, ldap_filter
        )
        if rdata:
            dn, ldap_attrs = coder.decode(rdata[0])
            ldap_user_name = ldap_attrs.get("sAMAccountName", [""])[0]
            if servidor.user:
                if User.objects.filter(username=ldap_user_name).exists():
                    user_target = User.objects.get(username=ldap_user_name)
                    mescla_users(servidor.user, user_target)
                    valid_users[dn] = user_target
                else:
                    update_user_from_ldap(servidor.user, ldap_attrs)
                    valid_users[dn] = servidor.user
            else:
                if User.objects.filter(username=ldap_user_name).exists():
                    servidor.user = User.objects.get(username=ldap_user_name)
                    servidor.save()
                    valid_users[dn] = servidor.user
                else:
                    servidor.ldap_dn = dn
                    servidor.save()

    # Eliminar servidores e seus usuários que não têm nenhum vínculo no sigi
    # e não constam na lista de valid_users

    print("\tRemoving inactive users and servidores")

    filter = (
        Q(externo=False)
        & Q(casas_que_gerencia=None)
        & Q(chefe=None)
        & Q(comentario=None)
        & Q(convenio=None)
        & Q(convenios_acompanhados=None)
        & Q(equipe_evento=None)
        & Q(itemsolicitado=None)
        & Q(modulo_apresentador=None)
        & Q(modulo_monitor=None)
        & Q(ocorrencia=None)
        & Q(orgao=None)
        & Q(solicitacao=None)
    )

    inativos = Servidor.objects.filter(filter).exclude(
        user__in=valid_users.values()
    )

    removed = User.objects.filter(servidor__in=inativos).delete()
    print(
        "\n".join(
            [
                f"\t\t{value} {key} records removed."
                for key, value in removed[1].items()
            ]
        )
    )
    removed = inativos.delete()
    print(
        "\n".join(
            [
                f"\t\t{value} {key} records removed."
                for key, value in removed[1].items()
            ]
        )
    )

    # Tratar os usuários que têm entrada de log mas não têm Servidor atribuído

    for user in User.objects.filter(servidor=None, is_active=True).exclude(
        logentry=None
    ):
        nome_completo = user.get_full_name().strip().lower() or user.username
        filter = [
            Q(nome_completo__icontains=to_ascii(n.strip()))
            for n in nome_completo.split(" ")
        ]
        try:
            # Tenta encontrar um servidor que tenha o mesmo nome e transferir
            # todo o log para o usuário desse servidor.
            servidor = Servidor.objects.get(*filter)
            if servidor.user:
                mescla_users(user, servidor.user)
                print(
                    f"\tUser {user.username} deleted. "
                    f"Logs to {servidor.user.username}"
                )
            else:
                servidor.user = user
                servidor.save()
                print(
                    f"\tUser {user.username} linked to "
                    f"servidor {servidor.nome_completo}"
                )
        except Servidor.DoesNotExist:
            # Realmente não possui um servidor com o mesmo nome. O que resta é
            # desativar o usuário para que não possa fazer login
            user.is_active = False
            user.save()
            print(f"\tUser {user.username} deactivated.")

    # Atualizar o campo ldap_dn dos servidores ativos do ILB
    print("\tUpdating ldap_dn field in servidor objects...", end=" ")
    ldap_filter = (
        "(&(department=*ILB*)(!(title=*Desligad*))(!(title=*inativ*)))"
    )
    page_control = ldap.controls.SimplePagedResultsControl(
        True, size=1000, cookie=""
    )
    updated = 0

    while True:
        response = connect.search_ext(
            settings.AUTH_LDAP_USER,
            ldap.SCOPE_ONELEVEL,
            ldap_filter,
            serverctrls=[page_control],
        )

        rtype, rdata, rmsgid, serverctrls = connect.result3(response)
        decoded_data = coder.decode(rdata)

        controls = [
            control
            for control in serverctrls
            if control.controlType
            == ldap.controls.SimplePagedResultsControl.controlType
        ]
        if not controls:
            raise Exception("The LDAP server ignores RFC 2696 control")

        for dn, ldap_user in decoded_data:
            user_name = ldap_user.get("sAMAccountName", [""])[0]
            if User.objects.filter(username=user_name).exists():
                user = User.objects.get(username=user_name)
                servidor = user.servidor
                if servidor:
                    servidor.ldap_dn = dn
                    servidor.save()
                    updated += 1

        if not controls[0].cookie:
            break
        page_control.cookie = controls[0].cookie

    print(f"{updated} servidores updated.")

    # Mesclar usuários duplicados
    print("\tJoin duplicated users ...")
    joined = 0

    for user in User.objects.exclude(Q(first_name="") & Q(last_name="")):
        query = User.objects.filter(
            first_name__iexact=user.first_name,
            last_name__iexact=user.last_name,
        ).exclude(id=user.id)
        if query.exists():
            user2 = query.get()
            dn1 = user.servidor.ldap_dn if user.servidor else ""

            if dn1:
                print(f"\t\t{user2} > {user}")
                mescla_users(user_source=user2, user_target=user)
            else:
                print(f"\t\t{user} > {user2}")
                mescla_users(user_source=user, user_target=user2)

    # Vincular servidores com seu distinguishedName no LDAP, se existir

    print("\tLink servidor with LDAP by distinguishedNames ... ")

    for servidor in Servidor.objects.filter(externo=False, ldap_dn=""):
        if servidor.user:
            rdata = connect.search_s(
                settings.AUTH_LDAP_USER,
                ldap.SCOPE_SUBTREE,
                ldap.filter.filter_format(
                    "(sAMAccountName=%s)", [servidor.user.username]
                ),
            )
        else:
            rdata = connect.search_s(
                settings.AUTH_LDAP_USER,
                ldap.SCOPE_SUBTREE,
                ldap.filter.filter_format(
                    "(cn=%s*)", [servidor.nome_completo]
                ),
            )
        if rdata:
            servidor.ldap_dn = coder.decode(rdata[0][0])
            servidor.save()
            print(f"\t\t{servidor.nome_completo} > {servidor.ldap_dn}")

    manuais = [
        (1139, 1147),  # Ricardo de Oliveira Murta
        (1129, 274),  # Adalberto Alves de Oliveira
        (1134, 166),  # Cláudio Morale
        (1130, 108),  # Janary Carvão Nunes
    ]

    for source_id, target_id in manuais:
        try:
            servidor_source = Servidor.objects.get(id=source_id)
            servidor_target = Servidor.objects.get(id=target_id)
        except Servidor.DoesNotExist:
            # Se um não existe, não há nada a fazer
            continue
        print(
            f"\tJoining {servidor_source.nome_completo} "
            f"to {servidor_target.nome_completo}"
        )
        mescla_servidores(servidor_source, servidor_target)


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0001_initial"),
        ("servidores", "0014_servidor_ldap_dn_alter_servidor_user"),
    ]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
