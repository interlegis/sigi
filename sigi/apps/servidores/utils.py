# Define algumas funções para manutenção de usuários e servidores

import ldap
from django.contrib.auth.models import Group
from django.conf import settings
from django.db.models import F
from django.db.models.fields.reverse_related import (
    ForeignObjectRel,
    ManyToOneRel,
    ManyToManyRel,
)
from django.forms.models import model_to_dict
from sigi.apps.servidores.models import Servidor, Servico


def _message_out(message, verbose):
    """_message_out Imprime mensagem apenas em modo verboso

    Arguments:
        message -- Mensagem
        verbose -- True para imprimir, False para não imprimir
    """
    if verbose:
        print(message)


def mescla_users(user_source, user_target, verbose=False):
    """mescla_users
    Transfere todos os dados de user_source para user_target e exclui
    user_target e o servidor vinculado a ele.

    Arguments:
        user_source -- Usuário a ser eliminado
        user_target -- Usuário que receberá os dados de user_source

    Keyword Arguments:
        verbose -- Se True, imprime mensagens de progresso (default: {False})
    """
    servidor_source = user_source.servidor
    servidor_target = user_target.servidor

    # Transfere registros de log
    _message_out("Transferring log entries...", verbose)
    user_source.logentry_set.update(user=user_target)

    # Se a origem não tem servidor, só resta matá-lo agora

    if servidor_source is None:
        user_source.delete()
        _message_out(f"User {user_source.username} deleted!", verbose)
        return

    # Se só a origem tem servidor
    if servidor_source and not servidor_target:
        # transfere o servidor inteiro e pronto
        servidor_source.user = user_target
        servidor_source.save()
        _message_out(
            f"Servidor {servidor_source.nome_completo} transferred "
            f"to {user_target.username}",
            verbose,
        )
        user_source.delete()
        _message_out(f"User {user_source.username} deleted!", verbose)
        return

    # Só chega aqui se ambos tiverem servidor vinculado

    _message_out("Merging servidores...", verbose)

    mescla_servidores(servidor_source, servidor_target, verbose)


def mescla_servidores(servidor_source, servidor_target, verbose=False):
    """mescla_servidor
    Transfere todos os dados de servidor_source para servidor_target e exclui
    servidor_target e o user vinculado a ele.


    Arguments:
        servidor_source -- Servidor a ser eliminado
        servidor_target -- Servidor que receberá os dados de servidor_source

    Keyword Arguments:
        verbose -- Se True, imprime mensagens de progresso (default: {False})
    """

    user_source = servidor_source.user
    user_target = servidor_target.user

    for field in Servidor._meta.get_fields():
        if not isinstance(field, ForeignObjectRel):
            continue

        accessor = field.get_accessor_name()
        remote_field = field.remote_field.name

        if isinstance(field, ManyToOneRel):
            getattr(servidor_source, accessor).update(
                **{remote_field: servidor_target}
            )
            _message_out(
                f"Updating field {remote_field} in "
                f"{field.remote_field.model._meta.verbose_name} "
                f"to {servidor_target}",
                verbose,
            )
        if isinstance(field, ManyToManyRel):
            for obj in getattr(servidor_source, accessor).all():
                getattr(servidor_target, accessor).add(obj)
                getattr(servidor_source, accessor).remove(obj)
                _message_out(
                    f"Transferring {obj} from source {accessor} "
                    f"to {servidor_target}",
                    verbose,
                )

    # Log dos usuários
    if user_source and not user_target:
        servidor_target.user = user_source
        _message_out(
            f"Target has no user. Transferring user {user_source.username} "
            "from source",
            verbose,
        )
    elif user_source and user_target:
        user_source.logentry_set.update(user=user_target)
        _message_out(
            f"Transferring {user_source.username} logentries "
            f"to {user_target.username}",
            verbose,
        )
        user_source.delete()
        _message_out(f"{user_source.username} deleted", verbose)

    servidor_source.delete()
    _message_out(f"{servidor_source.nome_completo} deleted", verbose)


def user_staff_and_group(user, ldap_attrs):
    dep = ldap_attrs.get("department", [""])[0]
    title = ldap_attrs.get("title", [""])[0]
    deps = dep.split("-")
    titles = [s.strip().upper() for s in title.split("-", 1)]
    group_names = [f"{d}-{t}" for d in deps for t in titles]
    group_names.extend(deps)
    group_names.extend(titles)
    group_names.extend([dep, title.upper()])
    user.is_staff = "ILB" in dep
    user.save()
    user.groups.clear()
    if user.is_staff:
        # Só cria grupos para o ILB #
        for name in group_names:
            group, created = Group.objects.get_or_create(name=name)
            user.groups.add(group)


def servidor_update_from_ldap(servidor, ldap_attrs, commit=True):
    sigla_servico = ldap_attrs.get("department", [""])[0].split("-")[-1]
    nome_cargo = ldap_attrs.get("title", [""])[0].split("-")[-1].strip()
    nome_completo = ldap_attrs.get("name", [""])[0]
    dn = ldap_attrs.get("distinguishedName", [""])[0]
    cargo = f"{nome_cargo} - {sigla_servico}"
    servico = Servico.objects.filter(sigla=sigla_servico).first()

    initial = model_to_dict(servidor)

    servidor.nome_completo = nome_completo
    servidor.servico = servico
    servidor.cargo = cargo
    servidor.ldap_dn = dn

    if servico is not None and nome_cargo.lower() in [
        "chefe de serviço",
        "coordenador",
    ]:
        servidor.save()  # Commit is needed to update servico instance
        servico.responsavel = servidor
        servico.save()
    elif commit:
        servidor.save()

    return (
        servidor_create_or_update.UNCHANGED
        if initial == model_to_dict(servidor)
        else servidor_create_or_update.UPDATED
    )


def servidor_create_or_update(ldap_attrs, commit=True):
    dn = ldap_attrs.get("distinguishedName", [""])[0]

    if dn != "" and Servidor.objects.filter(ldap_dn=dn).exists():
        servidor = Servidor.objects.get(ldap_dn=dn)
        result_code = servidor_update_from_ldap(servidor, ldap_attrs, commit)
    else:
        servidor = Servidor()
        servidor_update_from_ldap(servidor, ldap_attrs, commit)
        result_code = servidor_create_or_update.CREATED

    return (result_code, servidor)


servidor_create_or_update.UNCHANGED = "unchanged"
servidor_create_or_update.UPDATED = "updated"
servidor_create_or_update.CREATED = "created"
