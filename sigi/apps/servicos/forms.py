from django.forms.models import ModelForm
from django.utils.encoding import force_str
from sigi.apps.servicos.models import Servico, CasaAtendida


class ServicoFormAdmin(ModelForm):
    class Meta:
        model = Servico
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ServicoFormAdmin, self).__init__(*args, **kwargs)

        self.fields["contato_tecnico"].choices = ()
        self.fields["contato_administrativo"].choices = ()

        if self.instance.casa_legislativa_id:
            id_casa = self.instance.casa_legislativa_id
        elif "initial" in kwargs and "id_casa" in kwargs["initial"]:
            id_casa = kwargs["initial"]["id_casa"]
            self.instance.casa_legislativa_id = id_casa
        else:
            id_casa = None

        if id_casa:
            casa = CasaAtendida.objects.get(pk=id_casa)
            contatos = [
                (f.id, force_str(f)) for f in casa.funcionario_set.all()
            ]
            self.fields["contato_tecnico"].choices = contatos
            self.fields["contato_administrativo"].choices = contatos
