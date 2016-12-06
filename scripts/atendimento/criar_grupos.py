from django.contrib.auth.models import Group


def criar_grupos():
    # COPLAF = Atestar usuário
    if not Group.objects.filter(name='COPLAF').exists():
        Group.objects.create(name='COPLAF')

    # COADFI = Atestar convênio
    if not Group.objects.filter(name='COADFI').exists():
        Group.objects.create(name='COADFI')

    # Já recebeu aprovação dos dois grupos de cima
    if not Group.objects.filter(name='Usuario_Habilitado').exists():
        Group.objects.create(name='Usuario_Habilitado')
