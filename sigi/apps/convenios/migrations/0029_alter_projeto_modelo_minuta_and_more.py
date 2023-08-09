# Generated by Django 4.0.4 on 2022-06-21 22:24

import django.core.validators
from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):
    dependencies = [
        ("convenios", "0028_alter_projeto_modelo_minuta_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projeto",
            name="modelo_minuta",
            field=models.FileField(
                blank=True,
                help_text='\nUtilize os seguintes <a class="modal-trigger" href="#help_modal_modelo_minuta"><i>placeholders</i></a>\n<div id="help_modal_modelo_minuta" class="modal">\n  <div class="modal-content">\n    <h5>Placeholders</h5>\n    <ul class="collection">\n      \n      <li class="collection-item"><b>{{ evento }}</b>: Evento</li>\n      \n      <li class="collection-item"><b>{{ evento.nome }}</b>: Nome do evento</li>\n      \n      <li class="collection-item"><b>{{ evento.descricao }}</b>: Descrição do evento</li>\n      \n      <li class="collection-item"><b>{{ evento.virtual }}</b>: Virtual</li>\n      \n      <li class="collection-item"><b>{{ evento.solicitante }}</b>: Solicitante</li>\n      \n      <li class="collection-item"><b>{{ evento.num_processo }}</b>: número do processo SIGAD</li>\n      \n      <li class="collection-item"><b>{{ evento.data_pedido }}</b>: Data do pedido</li>\n      \n      <li class="collection-item"><b>{{ evento.data_inicio }}</b>: Data/hora do Início</li>\n      \n      <li class="collection-item"><b>{{ evento.data_termino }}</b>: Data/hora do Termino</li>\n      \n      <li class="collection-item"><b>{{ evento.carga_horaria }}</b>: carga horária</li>\n      \n      <li class="collection-item"><b>{{ evento.local }}</b>: Local do evento</li>\n      \n      <li class="collection-item"><b>{{ evento.observacao }}</b>: Observações e anotações</li>\n      \n      <li class="collection-item"><b>{{ evento.publico_alvo }}</b>: Público alvo</li>\n      \n      <li class="collection-item"><b>{{ evento.total_participantes }}</b>: Total de participantes</li>\n      \n      <li class="collection-item"><b>{{ evento.status }}</b>: Status</li>\n      \n      <li class="collection-item"><b>{{ evento.data_cancelamento }}</b>: Data de cancelamento</li>\n      \n      <li class="collection-item"><b>{{ evento.motivo_cancelamento }}</b>: Motivo do cancelamento</li>\n      \n      <li class="collection-item"><b>{{ casa }}</b>: Órgão</li>\n      \n      <li class="collection-item"><b>{{ casa.nome }}</b>: nome</li>\n      \n      <li class="collection-item"><b>{{ casa.sigla }}</b>: sigla do órgão</li>\n      \n      <li class="collection-item"><b>{{ casa.search_text }}</b>: search text</li>\n      \n      <li class="collection-item"><b>{{ casa.cnpj }}</b>: CNPJ</li>\n      \n      <li class="collection-item"><b>{{ casa.observacoes }}</b>: observações</li>\n      \n      <li class="collection-item"><b>{{ casa.horario_funcionamento }}</b>: horário de funcionamento da Casa Legislativa</li>\n      \n      <li class="collection-item"><b>{{ casa.codigo_interlegis }}</b>: código Interlegis</li>\n      \n      <li class="collection-item"><b>{{ casa.logradouro }}</b>: logradouro</li>\n      \n      <li class="collection-item"><b>{{ casa.bairro }}</b>: bairro</li>\n      \n      <li class="collection-item"><b>{{ casa.cep }}</b>: CEP</li>\n      \n      <li class="collection-item"><b>{{ casa.email }}</b>: e-mail</li>\n      \n      <li class="collection-item"><b>{{ casa.pagina_web }}</b>: página web</li>\n      \n      <li class="collection-item"><b>{{ casa.inclusao_digital }}</b>: inclusão digital</li>\n      \n      <li class="collection-item"><b>{{ casa.data_levantamento }}</b>: data/hora da pesquisa</li>\n      \n      <li class="collection-item"><b>{{ casa.obs_pesquisa }}</b>: observações do pesquisador</li>\n      \n      <li class="collection-item"><b>{{ casa.ult_alt_endereco }}</b>: última alteração do endereço</li>\n      \n      <li class="collection-item"><b>{{ casa.foto }}</b>: foto</li>\n      \n      <li class="collection-item"><b>{{ casa.foto_largura }}</b>: foto largura</li>\n      \n      <li class="collection-item"><b>{{ casa.foto_altura }}</b>: foto altura</li>\n      \n      <li class="collection-item"><b>{{ casa.data_instalacao }}</b>: data de instalação da Casa Legislativa</li>\n      \n      <li class="collection-item"><b>{{ casa.brasao }}</b>: brasão</li>\n      \n      <li class="collection-item"><b>{{ casa.brasao_largura }}</b>: brasao largura</li>\n      \n      <li class="collection-item"><b>{{ casa.brasao_altura }}</b>: brasao altura</li>\n      \n      <li class="collection-item"><b>{{ presidente }}</b>: Parlamentar</li>\n      \n      <li class="collection-item"><b>{{ presidente.ano_eleicao }}</b>: Ano de eleição</li>\n      \n      <li class="collection-item"><b>{{ presidente.status_mandato }}</b>: status do mandato</li>\n      \n      <li class="collection-item"><b>{{ presidente.presidente }}</b>: presidente</li>\n      \n      <li class="collection-item"><b>{{ presidente.nome_completo }}</b>: nome completo</li>\n      \n      <li class="collection-item"><b>{{ presidente.nome_parlamentar }}</b>: nome parlamentar</li>\n      \n      <li class="collection-item"><b>{{ presidente.foto }}</b>: foto</li>\n      \n      <li class="collection-item"><b>{{ presidente.foto_largura }}</b>: foto largura</li>\n      \n      <li class="collection-item"><b>{{ presidente.foto_altura }}</b>: foto altura</li>\n      \n      <li class="collection-item"><b>{{ presidente.data_nascimento }}</b>: data de nascimento</li>\n      \n      <li class="collection-item"><b>{{ presidente.cpf }}</b>: CPF</li>\n      \n      <li class="collection-item"><b>{{ presidente.identidade }}</b>: Identidade (RG)</li>\n      \n      <li class="collection-item"><b>{{ presidente.telefones }}</b>: telefones</li>\n      \n      <li class="collection-item"><b>{{ presidente.email }}</b>: e-mail</li>\n      \n      <li class="collection-item"><b>{{ presidente.redes_sociais }}</b>: redes sociais</li>\n      \n      <li class="collection-item"><b>{{ presidente.ult_alteracao }}</b>: última alteração</li>\n      \n      <li class="collection-item"><b>{{ presidente.observacoes }}</b>: observações</li>\n      \n      <li class="collection-item"><b>{{ presidente.sequencial_tse }}</b>: Sequencial TSE</li>\n      \n      <li class="collection-item"><b>{{ presidente.flag_importa }}</b>: flag importa</li>\n      \n      <li class="collection-item"><b>{{ contato }}</b>: Contato da casa legislativa</li>\n      \n      <li class="collection-item"><b>{{ contato.nome }}</b>: nome completo</li>\n      \n      <li class="collection-item"><b>{{ contato.sexo }}</b>: sexo</li>\n      \n      <li class="collection-item"><b>{{ contato.data_nascimento }}</b>: data de nascimento</li>\n      \n      <li class="collection-item"><b>{{ contato.cpf }}</b>: CPF</li>\n      \n      <li class="collection-item"><b>{{ contato.identidade }}</b>: Identidade (RG)</li>\n      \n      <li class="collection-item"><b>{{ contato.nota }}</b>: telefones</li>\n      \n      <li class="collection-item"><b>{{ contato.email }}</b>: e-mail</li>\n      \n      <li class="collection-item"><b>{{ contato.endereco }}</b>: endereço</li>\n      \n      <li class="collection-item"><b>{{ contato.bairro }}</b>: bairro</li>\n      \n      <li class="collection-item"><b>{{ contato.cep }}</b>: CEP</li>\n      \n      <li class="collection-item"><b>{{ contato.redes_sociais }}</b>: redes sociais</li>\n      \n      <li class="collection-item"><b>{{ contato.cargo }}</b>: cargo</li>\n      \n      <li class="collection-item"><b>{{ contato.funcao }}</b>: função</li>\n      \n      <li class="collection-item"><b>{{ contato.setor }}</b>: setor</li>\n      \n      <li class="collection-item"><b>{{ contato.tempo_de_servico }}</b>: tempo de serviço</li>\n      \n      <li class="collection-item"><b>{{ contato.ult_alteracao }}</b>: última alteração</li>\n      \n      <li class="collection-item"><b>{{ contato.desativado }}</b>: desativado</li>\n      \n      <li class="collection-item"><b>{{ contato.observacoes }}</b>: observações</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio }}</b>: Município</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.codigo_ibge }}</b>: código IBGE</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.codigo_tse }}</b>: código TSE</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.nome }}</b>: nome</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.search_text }}</b>: search text</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.is_capital }}</b>: capital</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.populacao }}</b>: população</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.is_polo }}</b>: pólo</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.data_criacao }}</b>: data de criação do município</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.latitude }}</b>: latitude</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.longitude }}</b>: longitude</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.idh }}</b>: IDH</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.pib_total }}</b>: PIB total</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.pib_percapita }}</b>: PIB per capita</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.pib_ano }}</b>: Ano de apuração do PIB</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf }}</b>: Unidade federativa</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.codigo_ibge }}</b>: código IBGE</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.nome }}</b>: nome UF</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.search_text }}</b>: search text</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.sigla }}</b>: sigla</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.regiao }}</b>: região</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.populacao }}</b>: população</li>\n      \n      <li class="collection-item"><b>{{ data }}</b>: Data atual</li>\n      \n      <li class="collection-item"><b>{{ ente }}</b>: Ente da federação (município/estado)</li>\n      \n      <li class="collection-item"><b>{{ doravante }}</b>: CÂMARA ou ASSEMBLEIA</li>\n      \n    </ul>\n  </div>\n  <div class="modal-footer">\n    <a href="#!" class="modal-close waves-effect waves-green btn-small btn-flat">Fechar</a>\n  </div>\n</div>\n<script>\n  console.log("Rodou");\n  $(document).ready(function(){\n    M.Modal.init($(\'.modal\'), {});\n  });\n</script>',
                upload_to="convenios/minutas/",
                validators=[
                    django.core.validators.FileExtensionValidator(["docx"])
                ],
                verbose_name="Modelo de minuta",
            ),
        ),
        migrations.AlterField(
            model_name="projeto",
            name="texto_oficio",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text='\nUtilize os seguintes <a class="modal-trigger" href="#help_modal_texto_oficio"><i>placeholders</i></a>\n<div id="help_modal_texto_oficio" class="modal">\n  <div class="modal-content">\n    <h5>Placeholders</h5>\n    <ul class="collection">\n      \n      <li class="collection-item"><b>{{ evento }}</b>: Evento</li>\n      \n      <li class="collection-item"><b>{{ evento.nome }}</b>: Nome do evento</li>\n      \n      <li class="collection-item"><b>{{ evento.descricao }}</b>: Descrição do evento</li>\n      \n      <li class="collection-item"><b>{{ evento.virtual }}</b>: Virtual</li>\n      \n      <li class="collection-item"><b>{{ evento.solicitante }}</b>: Solicitante</li>\n      \n      <li class="collection-item"><b>{{ evento.num_processo }}</b>: número do processo SIGAD</li>\n      \n      <li class="collection-item"><b>{{ evento.data_pedido }}</b>: Data do pedido</li>\n      \n      <li class="collection-item"><b>{{ evento.data_inicio }}</b>: Data/hora do Início</li>\n      \n      <li class="collection-item"><b>{{ evento.data_termino }}</b>: Data/hora do Termino</li>\n      \n      <li class="collection-item"><b>{{ evento.carga_horaria }}</b>: carga horária</li>\n      \n      <li class="collection-item"><b>{{ evento.local }}</b>: Local do evento</li>\n      \n      <li class="collection-item"><b>{{ evento.observacao }}</b>: Observações e anotações</li>\n      \n      <li class="collection-item"><b>{{ evento.publico_alvo }}</b>: Público alvo</li>\n      \n      <li class="collection-item"><b>{{ evento.total_participantes }}</b>: Total de participantes</li>\n      \n      <li class="collection-item"><b>{{ evento.status }}</b>: Status</li>\n      \n      <li class="collection-item"><b>{{ evento.data_cancelamento }}</b>: Data de cancelamento</li>\n      \n      <li class="collection-item"><b>{{ evento.motivo_cancelamento }}</b>: Motivo do cancelamento</li>\n      \n      <li class="collection-item"><b>{{ casa }}</b>: Órgão</li>\n      \n      <li class="collection-item"><b>{{ casa.nome }}</b>: nome</li>\n      \n      <li class="collection-item"><b>{{ casa.sigla }}</b>: sigla do órgão</li>\n      \n      <li class="collection-item"><b>{{ casa.search_text }}</b>: search text</li>\n      \n      <li class="collection-item"><b>{{ casa.cnpj }}</b>: CNPJ</li>\n      \n      <li class="collection-item"><b>{{ casa.observacoes }}</b>: observações</li>\n      \n      <li class="collection-item"><b>{{ casa.horario_funcionamento }}</b>: horário de funcionamento da Casa Legislativa</li>\n      \n      <li class="collection-item"><b>{{ casa.codigo_interlegis }}</b>: código Interlegis</li>\n      \n      <li class="collection-item"><b>{{ casa.logradouro }}</b>: logradouro</li>\n      \n      <li class="collection-item"><b>{{ casa.bairro }}</b>: bairro</li>\n      \n      <li class="collection-item"><b>{{ casa.cep }}</b>: CEP</li>\n      \n      <li class="collection-item"><b>{{ casa.email }}</b>: e-mail</li>\n      \n      <li class="collection-item"><b>{{ casa.pagina_web }}</b>: página web</li>\n      \n      <li class="collection-item"><b>{{ casa.inclusao_digital }}</b>: inclusão digital</li>\n      \n      <li class="collection-item"><b>{{ casa.data_levantamento }}</b>: data/hora da pesquisa</li>\n      \n      <li class="collection-item"><b>{{ casa.obs_pesquisa }}</b>: observações do pesquisador</li>\n      \n      <li class="collection-item"><b>{{ casa.ult_alt_endereco }}</b>: última alteração do endereço</li>\n      \n      <li class="collection-item"><b>{{ casa.foto }}</b>: foto</li>\n      \n      <li class="collection-item"><b>{{ casa.foto_largura }}</b>: foto largura</li>\n      \n      <li class="collection-item"><b>{{ casa.foto_altura }}</b>: foto altura</li>\n      \n      <li class="collection-item"><b>{{ casa.data_instalacao }}</b>: data de instalação da Casa Legislativa</li>\n      \n      <li class="collection-item"><b>{{ casa.brasao }}</b>: brasão</li>\n      \n      <li class="collection-item"><b>{{ casa.brasao_largura }}</b>: brasao largura</li>\n      \n      <li class="collection-item"><b>{{ casa.brasao_altura }}</b>: brasao altura</li>\n      \n      <li class="collection-item"><b>{{ presidente }}</b>: Parlamentar</li>\n      \n      <li class="collection-item"><b>{{ presidente.ano_eleicao }}</b>: Ano de eleição</li>\n      \n      <li class="collection-item"><b>{{ presidente.status_mandato }}</b>: status do mandato</li>\n      \n      <li class="collection-item"><b>{{ presidente.presidente }}</b>: presidente</li>\n      \n      <li class="collection-item"><b>{{ presidente.nome_completo }}</b>: nome completo</li>\n      \n      <li class="collection-item"><b>{{ presidente.nome_parlamentar }}</b>: nome parlamentar</li>\n      \n      <li class="collection-item"><b>{{ presidente.foto }}</b>: foto</li>\n      \n      <li class="collection-item"><b>{{ presidente.foto_largura }}</b>: foto largura</li>\n      \n      <li class="collection-item"><b>{{ presidente.foto_altura }}</b>: foto altura</li>\n      \n      <li class="collection-item"><b>{{ presidente.data_nascimento }}</b>: data de nascimento</li>\n      \n      <li class="collection-item"><b>{{ presidente.cpf }}</b>: CPF</li>\n      \n      <li class="collection-item"><b>{{ presidente.identidade }}</b>: Identidade (RG)</li>\n      \n      <li class="collection-item"><b>{{ presidente.telefones }}</b>: telefones</li>\n      \n      <li class="collection-item"><b>{{ presidente.email }}</b>: e-mail</li>\n      \n      <li class="collection-item"><b>{{ presidente.redes_sociais }}</b>: redes sociais</li>\n      \n      <li class="collection-item"><b>{{ presidente.ult_alteracao }}</b>: última alteração</li>\n      \n      <li class="collection-item"><b>{{ presidente.observacoes }}</b>: observações</li>\n      \n      <li class="collection-item"><b>{{ presidente.sequencial_tse }}</b>: Sequencial TSE</li>\n      \n      <li class="collection-item"><b>{{ presidente.flag_importa }}</b>: flag importa</li>\n      \n      <li class="collection-item"><b>{{ contato }}</b>: Contato da casa legislativa</li>\n      \n      <li class="collection-item"><b>{{ contato.nome }}</b>: nome completo</li>\n      \n      <li class="collection-item"><b>{{ contato.sexo }}</b>: sexo</li>\n      \n      <li class="collection-item"><b>{{ contato.data_nascimento }}</b>: data de nascimento</li>\n      \n      <li class="collection-item"><b>{{ contato.cpf }}</b>: CPF</li>\n      \n      <li class="collection-item"><b>{{ contato.identidade }}</b>: Identidade (RG)</li>\n      \n      <li class="collection-item"><b>{{ contato.nota }}</b>: telefones</li>\n      \n      <li class="collection-item"><b>{{ contato.email }}</b>: e-mail</li>\n      \n      <li class="collection-item"><b>{{ contato.endereco }}</b>: endereço</li>\n      \n      <li class="collection-item"><b>{{ contato.bairro }}</b>: bairro</li>\n      \n      <li class="collection-item"><b>{{ contato.cep }}</b>: CEP</li>\n      \n      <li class="collection-item"><b>{{ contato.redes_sociais }}</b>: redes sociais</li>\n      \n      <li class="collection-item"><b>{{ contato.cargo }}</b>: cargo</li>\n      \n      <li class="collection-item"><b>{{ contato.funcao }}</b>: função</li>\n      \n      <li class="collection-item"><b>{{ contato.setor }}</b>: setor</li>\n      \n      <li class="collection-item"><b>{{ contato.tempo_de_servico }}</b>: tempo de serviço</li>\n      \n      <li class="collection-item"><b>{{ contato.ult_alteracao }}</b>: última alteração</li>\n      \n      <li class="collection-item"><b>{{ contato.desativado }}</b>: desativado</li>\n      \n      <li class="collection-item"><b>{{ contato.observacoes }}</b>: observações</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio }}</b>: Município</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.codigo_ibge }}</b>: código IBGE</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.codigo_tse }}</b>: código TSE</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.nome }}</b>: nome</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.search_text }}</b>: search text</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.is_capital }}</b>: capital</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.populacao }}</b>: população</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.is_polo }}</b>: pólo</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.data_criacao }}</b>: data de criação do município</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.latitude }}</b>: latitude</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.longitude }}</b>: longitude</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.idh }}</b>: IDH</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.pib_total }}</b>: PIB total</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.pib_percapita }}</b>: PIB per capita</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.pib_ano }}</b>: Ano de apuração do PIB</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf }}</b>: Unidade federativa</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.codigo_ibge }}</b>: código IBGE</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.nome }}</b>: nome UF</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.search_text }}</b>: search text</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.sigla }}</b>: sigla</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.regiao }}</b>: região</li>\n      \n      <li class="collection-item"><b>{{ casa.municipio.uf.populacao }}</b>: população</li>\n      \n      <li class="collection-item"><b>{{ data }}</b>: Data atual</li>\n      \n      <li class="collection-item"><b>{{ doravante }}</b>: CÂMARA ou ASSEMBLEIA</li>\n      \n    </ul>\n  </div>\n  <div class="modal-footer">\n    <a href="#!" class="modal-close waves-effect waves-green btn-small btn-flat">Fechar</a>\n  </div>\n</div>\n<script>\n  console.log("Rodou");\n  $(document).ready(function(){\n    M.Modal.init($(\'.modal\'), {});\n  });\n</script>',
                verbose_name="texto do ofício",
            ),
        ),
    ]
