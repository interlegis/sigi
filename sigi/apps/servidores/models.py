from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.utils.translation import gettext as _
from django_auth_ldap.backend import populate_user, LDAPBackend


class Servico(models.Model):
    nome = models.CharField(_("Setor"), max_length=250, null=True)
    sigla = models.CharField(max_length=10, null=True)
    subordinado = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("subordinado a"),
    )
    responsavel = models.ForeignKey(
        "servidores.Servidor",
        on_delete=models.SET_NULL,
        related_name="chefe",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = (
            "-subordinado__sigla",
            "nome",
        )
        verbose_name = _("serviço")
        verbose_name_plural = _("serviços")

    def __str__(self):
        return f"{self.sigla} - {self.nome}"


class Servidor(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    nome_completo = models.CharField(max_length=128)
    apelido = models.CharField(max_length=50, blank=True)
    foto = models.ImageField(
        upload_to="fotos/servidores",
        width_field="foto_largura",
        height_field="foto_altura",
        blank=True,
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    servico = models.ForeignKey(
        Servico, on_delete=models.SET_NULL, blank=True, null=True
    )
    cargo = models.CharField(max_length=100, blank=True)
    externo = models.BooleanField(_("colaborador externo"), default=False)
    orgao_origem = models.CharField(
        _("órgão de origem, "), max_length=100, blank=True
    )
    qualificacoes = models.TextField(_("qualificações"), blank=True)
    sigi = models.BooleanField(
        _("Servidor SIGI"), default=False, editable=False
    )

    class Meta:
        ordering = ("nome_completo",)
        verbose_name_plural = "servidores"

    def __str__(self):
        return self.nome_completo

    def save(self, *args, **kwargs):
        if self.user is not None:
            Servidor.objects.filter(user=self.user).update(user=None)
        return super(Servidor, self).save(*args, **kwargs)

    def get_apelido(self):
        if self.apelido:
            return self.apelido
        else:
            nomes = self.nome_completo.split(" ")
            return nomes[0]


# Soluçao alternativa para extender o usuário do django
# Acessa do servidor de um objeto user criando um profile
# baseado nos dados do LDAP
User.servidor = property(
    lambda user: Servidor.objects.get(user=user)
    if Servidor.objects.filter(user=user).exists()
    else None
)

# Sinal para ao criar um usuário criar um servidor
# baseado no nome contido no LDAP
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if not hasattr(instance, "ldap_user"):
        return
    sigla_servico = instance.ldap_user.attrs.get("department", [""])[0].split(
        "-"
    )[-1]
    servico = Servico.objects.filter(sigla=sigla_servico).first()
    if created and instance.is_staff:
        Servidor.objects.create(
            user=instance,
            nome_completo="%s %s" % (instance.first_name, instance.last_name),
            servico=servico,
        )
    elif (
        not created
        and instance.is_staff
        and instance.servidor is not None
        and instance.servidor.servico != servico
    ):
        servidor = instance.servidor
        servidor.servico = servico
        servidor.save()


# Hack horrível para ajustar o first_name e o last_name do User criado pelo
# Django-ldap. Os campos first_name e last_name têm o tamanho máximo de
# 30 caracteres, mas o LDAP não tem esse limite, e alguns usuários podem ter
# nomes maiores que isso, o que provoca erro ao salvar o usuário.
@receiver(pre_save, sender=User)
def ajusta_nome_usuario(sender, instance, *args, **kwargs):
    instance.first_name = instance.first_name[:30]
    instance.last_name = instance.last_name[:30]


# Identifica se um usuário do LDAP é membro da equipe (is_staff) verificando se
# a propriedade Department, do LDAP, é uma unidade do ILB. Também desmembra
# o campo Department para gerar os nomes dos grupos que o User vai integrar
@receiver(populate_user, sender=LDAPBackend)
def user_staff_and_group(user, ldap_user, **kwargs):
    dep = ldap_user.attrs.get("department", [""])[0]
    title = ldap_user.attrs.get("title", [""])[0]
    group_names = [dep.split("-")[-1], title]
    group_names.extend(title.split("-", 1))
    group_names = [s.strip().upper() for s in group_names]
    user.is_staff = "ILB" in dep
    user.save()
    user.groups.clear()
    for name in group_names:
        group, created = Group.objects.get_or_create(name=name)
        user.groups.add(group)
