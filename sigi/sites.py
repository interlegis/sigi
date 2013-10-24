from django.contrib.auth.admin import Group, GroupAdmin, User, UserAdmin
from django.contrib.sites.admin import Site, SiteAdmin
from django.contrib.admin.sites import AdminSite
from treemenus.admin import Menu, MenuAdmin
from sigi.apps.casas.admin import CasaLegislativa, CasaLegislativaAdmin
from sigi.apps.contatos.admin import (UnidadeFederativa, UnidadeFederativaAdmin,
                                      Municipio, MunicipioAdmin, Telefone,
                                      TelefoneAdmin, Contato, ContatoAdmin)
from sigi.apps.convenios.admin import (Projeto, Convenio, ConvenioAdmin, EquipamentoPrevisto,
                                       EquipamentoPrevistoAdmin, Anexo, AnexoAdmin,
                                       UnidadeAdministrativa,Tramitacao)
from sigi.apps.inventario.admin import (Fornecedor, FornecedorAdmin, Fabricante,
                                        FabricanteAdmin, Equipamento,
                                        EquipamentoAdmin, TipoEquipamento,
                                        TipoEquipamentoAdmin, ModeloEquipamento,
                                        ModeloEquipamentoAdmin, Bem, BemAdmin)
from sigi.apps.servicos.admin import (TipoServico, TipoServicoAdmin, CasaAtendida,
                            CasaAtendidaAdmin, Servico, ServicoAdmin)
from sigi.apps.mesas.admin import (Legislatura, LegislaturaAdmin, Coligacao,
                                   ColigacaoAdmin, ComposicaoColigacao,
                                   ComposicaoColigacaoAdmin, SessaoLegislativa,
                                   SessaoLegislativaAdmin, MesaDiretora,
                                   MesaDiretoraAdmin, Cargo, CargoAdmin,
                                   MembroMesaDiretora, MembroMesaDiretoraAdmin)
from sigi.apps.parlamentares.admin import (Partido, PartidoAdmin, Parlamentar,
                                           ParlamentarAdmin, Mandato, MandatoAdmin)
from sigi.apps.diagnosticos.admin import (Diagnostico, DiagnosticoAdmin, Pergunta,
                                          PerguntaAdmin, Escolha, EscolhaAdmin, Anexo as AnexoDiagnostico,
                                          AnexoAdmin as AnexoDiagnosticoAdmin, Categoria as
                                          CategoriaDiagnostico)
from sigi.apps.servidores.admin import (Servidor, ServidorAdmin, Funcao, FuncaoAdmin,
                                        Ferias, FeriasAdmin, Licenca, LicencaAdmin)
from sigi.apps.ocorrencias.admin import (Ocorrencia, OcorrenciaAdmin, Categoria, TipoContato)
from sigi.apps.eventos.admin import (Recurso, RecursoAdmin)
from sigi.apps.metas.admin import (Meta, MetaAdmin, PlanoDiretor, PlanoDiretorAdmin)
from sigi.apps.financeiro.admin import (Desembolso, DesembolsoAdmin)
from apps.casas.models import TipoCasaLegislativa

class DefaultSite(AdminSite):
    index_template = 'index.html'
    login_template = 'login.html'
    app_index_template = 'app_index.html'

default = DefaultSite()

# django.contrib.auth
default.register(Group, GroupAdmin)
default.register(User, UserAdmin)

# django.contrib.sites
default.register(Site, SiteAdmin)

# treemenus
default.register(Menu, MenuAdmin)

# sigi.apps.casas
default.register(TipoCasaLegislativa)
default.register(CasaLegislativa, CasaLegislativaAdmin)

# sigi.apps.contatos
default.register(UnidadeFederativa, UnidadeFederativaAdmin)
default.register(Municipio, MunicipioAdmin)
default.register(Telefone, TelefoneAdmin)
default.register(Contato, ContatoAdmin)

# sigi.apps.convenios
default.register(Projeto)
default.register(Convenio, ConvenioAdmin)
default.register(EquipamentoPrevisto, EquipamentoPrevistoAdmin)
default.register(Anexo, AnexoAdmin)
default.register(UnidadeAdministrativa)
default.register(Tramitacao)

# sigi.apps.inventario
default.register(Fornecedor, FornecedorAdmin)
default.register(Fabricante, FabricanteAdmin)
default.register(TipoEquipamento, TipoEquipamentoAdmin)
default.register(ModeloEquipamento,ModeloEquipamentoAdmin)
default.register(Equipamento, EquipamentoAdmin)
default.register(Bem, BemAdmin)

# sigi.apps.servicos
default.register(TipoServico, TipoServicoAdmin)
default.register(Servico, ServicoAdmin)
default.register(CasaAtendida, CasaAtendidaAdmin)

# sigi.apps.mesas
default.register(Legislatura, LegislaturaAdmin)
default.register(Coligacao, ColigacaoAdmin)
default.register(ComposicaoColigacao, ComposicaoColigacaoAdmin)
default.register(SessaoLegislativa, SessaoLegislativaAdmin)
default.register(MesaDiretora, MesaDiretoraAdmin)
default.register(Cargo, CargoAdmin)
default.register(MembroMesaDiretora, MembroMesaDiretoraAdmin)

# sigi.apps.parlamentares
default.register(Partido, PartidoAdmin)
default.register(Parlamentar, ParlamentarAdmin)
default.register(Mandato, MandatoAdmin)

# sigi.apps.diagnosticos
default.register(Diagnostico, DiagnosticoAdmin)
default.register(Pergunta, PerguntaAdmin)
default.register(Escolha, EscolhaAdmin)
default.register(AnexoDiagnostico, AnexoDiagnosticoAdmin)
default.register(CategoriaDiagnostico)

# sigi.apps.servidores
default.register(Servidor, ServidorAdmin)
default.register(Funcao, FuncaoAdmin)
default.register(Ferias, FeriasAdmin)
default.register(Licenca, LicencaAdmin)

# sigi.apps.ocorrencias
default.register(Ocorrencia, OcorrenciaAdmin)
default.register(Categoria)
default.register(TipoContato)

# sigi.apps.eventos
default.register(Recurso, RecursoAdmin)

# sigi.apps.metas
default.register(Meta, MetaAdmin)
default.register(PlanoDiretor, PlanoDiretorAdmin)

# sigi.apps.financeiro
default.register(Desembolso, DesembolsoAdmin)