BEGIN;
CREATE TABLE "servicos_servico" (
    "id" integer NOT NULL PRIMARY KEY,
    "titulo" varchar(60) NOT NULL,
    "tipo" varchar(30) NOT NULL,
    "descricao" text NOT NULL,
    "data_inicio" date NULL,
    "data_fim" date NULL,
    "situacao" varchar(1) NOT NULL,
    "avaliacao" smallint unsigned NULL
)
;
COMMIT;
BEGIN;
CREATE TABLE "casas_casalegislativa" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome" varchar(60) NOT NULL,
    "sigla" varchar(30) NOT NULL,
    "tipo" varchar(2) NOT NULL,
    "cnpj" varchar(18) NOT NULL,
    "logradouro" varchar(100) NOT NULL,
    "bairro" varchar(40) NOT NULL,
    "municipio_id" integer NOT NULL REFERENCES "contatos_municipio" ("codigo_ibge"),
    "cep" varchar(9) NOT NULL,
    "email" varchar(75) NOT NULL,
    "pagina_web" varchar(200) NOT NULL,
    "foto" varchar(100) NOT NULL,
    "foto_largura" smallint NULL,
    "foto_altura" smallint NULL,
    "historico" text NOT NULL
)
;
COMMIT;
BEGIN;
CREATE TABLE "contatos_unidadefederativa" (
    "codigo_ibge" integer unsigned NOT NULL PRIMARY KEY,
    "nome" varchar(25) NOT NULL,
    "sigla" varchar(2) NOT NULL UNIQUE,
    "regiao" varchar(2) NOT NULL,
    "populacao" integer unsigned NOT NULL
)
;
CREATE TABLE "contatos_municipio" (
    "codigo_ibge" integer unsigned NOT NULL PRIMARY KEY,
    "codigo_mesorregiao" integer unsigned NOT NULL,
    "codigo_microrregiao" integer unsigned NOT NULL,
    "nome" varchar(50) NOT NULL,
    "uf_id" integer NOT NULL REFERENCES "contatos_unidadefederativa" ("codigo_ibge"),
    "is_capital" bool NOT NULL,
    "populacao" integer unsigned NOT NULL,
    "is_polo" bool NOT NULL,
    "latitude" decimal NULL,
    "longitude" decimal NULL
)
;
CREATE TABLE "contatos_telefone" (
    "id" integer NOT NULL PRIMARY KEY,
    "codigo_ddd" varchar(2) NOT NULL,
    "numero" varchar(9) NOT NULL,
    "tipo" varchar(1) NOT NULL,
    "nota" varchar(70) NOT NULL,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL,
    UNIQUE ("codigo_ddd", "numero", "tipo")
)
;
CREATE TABLE "contatos_contato" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome" varchar(60) NOT NULL,
    "nota" varchar(70) NOT NULL,
    "email" varchar(75) NOT NULL,
    "municipio_id" integer NULL REFERENCES "contatos_municipio" ("codigo_ibge"),
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
    "object_id" integer unsigned NOT NULL
)
;
COMMIT;
BEGIN;
CREATE TABLE "convenios_convenio" (
    "id" integer NOT NULL PRIMARY KEY,
    "casa_legislativa_id" integer NOT NULL REFERENCES "casas_casalegislativa" ("id"),
    "num_convenio" integer unsigned NOT NULL,
    "num_processo_sf" varchar(11) NOT NULL,
    "data_adesao" date NOT NULL,
    "data_retorno_assinatura" date NULL,
    "data_termo_aceite" date NULL,
    "data_pub_diario" date NULL,
    "equipamentos_recebidos" varchar(1) NOT NULL
)
;
CREATE TABLE "convenios_equipamentoprevisto" (
    "id" integer NOT NULL PRIMARY KEY,
    "convenio_id" integer NOT NULL REFERENCES "convenios_convenio" ("id"),
    "equipamento_id" integer NOT NULL REFERENCES "inventario_equipamento" ("id"),
    "quantidade" smallint unsigned NOT NULL
)
;
CREATE TABLE "convenios_anexo" (
    "id" integer NOT NULL PRIMARY KEY,
    "convenio_id" integer NOT NULL REFERENCES "convenios_convenio" ("id"),
    "arquivo" varchar(100) NOT NULL,
    "descricao" varchar(70) NOT NULL,
    "data_pub" datetime NOT NULL
)
;
CREATE TABLE "convenios_convenio_servicos" (
    "id" integer NOT NULL PRIMARY KEY,
    "convenio_id" integer NOT NULL REFERENCES "convenios_convenio" ("id"),
    "servico_id" integer NOT NULL REFERENCES "servicos_servico" ("id"),
    UNIQUE ("convenio_id", "servico_id")
)
;
COMMIT;
BEGIN;
CREATE TABLE "inventario_fornecedor" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome" varchar(40) NOT NULL,
    "email" varchar(75) NOT NULL,
    "pagina_web" varchar(200) NOT NULL
)
;
CREATE TABLE "inventario_fabricante" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome" varchar(40) NOT NULL
)
;
CREATE TABLE "inventario_tipoequipamento" (
    "id" integer NOT NULL PRIMARY KEY,
    "tipo" varchar(40) NOT NULL
)
;
CREATE TABLE "inventario_modeloequipamento" (
    "id" integer NOT NULL PRIMARY KEY,
    "tipo_id" integer NOT NULL REFERENCES "inventario_tipoequipamento" ("id"),
    "modelo" varchar(30) NOT NULL
)
;
CREATE TABLE "inventario_equipamento" (
    "id" integer NOT NULL PRIMARY KEY,
    "fabricante_id" integer NOT NULL REFERENCES "inventario_fabricante" ("id"),
    "modelo_id" integer NOT NULL REFERENCES "inventario_modeloequipamento" ("id"),
    UNIQUE ("fabricante_id", "modelo_id")
)
;
CREATE TABLE "inventario_bem" (
    "id" integer NOT NULL PRIMARY KEY,
    "casa_legislativa_id" integer NOT NULL REFERENCES "casas_casalegislativa" ("id"),
    "equipamento_id" integer NOT NULL REFERENCES "inventario_equipamento" ("id"),
    "fornecedor_id" integer NOT NULL REFERENCES "inventario_fornecedor" ("id"),
    "num_serie" varchar(50) NOT NULL UNIQUE,
    "num_tombamento" varchar(50) NOT NULL UNIQUE
)
;
COMMIT;
BEGIN;
CREATE TABLE "mesas_legislatura" (
    "id" integer NOT NULL PRIMARY KEY,
    "numero" smallint unsigned NOT NULL,
    "data_inicio" date NOT NULL,
    "data_fim" date NOT NULL,
    "data_eleicao" date NOT NULL
)
;
CREATE TABLE "mesas_coligacao" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome" varchar(50) NOT NULL,
    "legislatura_id" integer NOT NULL REFERENCES "mesas_legislatura" ("id"),
    "numero_votos" integer unsigned NULL
)
;
CREATE TABLE "mesas_composicaocoligacao" (
    "id" integer NOT NULL PRIMARY KEY,
    "coligacao_id" integer NOT NULL REFERENCES "mesas_coligacao" ("id"),
    "partido_id" integer NOT NULL REFERENCES "parlamentares_partido" ("id")
)
;
CREATE TABLE "mesas_sessaolegislativa" (
    "id" integer NOT NULL PRIMARY KEY,
    "numero" smallint unsigned NOT NULL UNIQUE,
    "mesa_diretora_id" integer NOT NULL,
    "legislatura_id" integer NOT NULL REFERENCES "mesas_legislatura" ("id"),
    "tipo" varchar(1) NOT NULL,
    "data_inicio" date NOT NULL,
    "data_fim" date NOT NULL,
    "data_inicio_intervalo" date NULL,
    "data_fim_intervalo" date NULL
)
;
CREATE TABLE "mesas_mesadiretora" (
    "id" integer NOT NULL PRIMARY KEY,
    "casa_legislativa_id" integer NOT NULL REFERENCES "casas_casalegislativa" ("id")
)
;
CREATE TABLE "mesas_cargo" (
    "id" integer NOT NULL PRIMARY KEY,
    "descricao" varchar(30) NOT NULL
)
;
CREATE TABLE "mesas_membromesadiretora" (
    "id" integer NOT NULL PRIMARY KEY,
    "parlamentar_id" integer NOT NULL REFERENCES "parlamentares_parlamentar" ("id"),
    "cargo_id" integer NOT NULL REFERENCES "mesas_cargo" ("id"),
    "mesa_diretora_id" integer NOT NULL REFERENCES "mesas_mesadiretora" ("id")
)
;
COMMIT;
BEGIN;
CREATE TABLE "parlamentares_partido" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome" varchar(50) NOT NULL,
    "sigla" varchar(10) NOT NULL
)
;
CREATE TABLE "parlamentares_parlamentar" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome_completo" varchar(60) NOT NULL,
    "nome_parlamentar" varchar(35) NOT NULL,
    "foto" varchar(100) NOT NULL,
    "foto_largura" smallint NULL,
    "foto_altura" smallint NULL,
    "sexo" varchar(1) NOT NULL,
    "data_nascimento" date NULL,
    "logradouro" varchar(100) NOT NULL,
    "bairro" varchar(40) NOT NULL,
    "municipio_id" integer NULL REFERENCES "contatos_municipio" ("codigo_ibge"),
    "cep" varchar(9) NOT NULL,
    "pagina_web" varchar(200) NOT NULL,
    "email" varchar(75) NOT NULL
)
;
CREATE TABLE "parlamentares_mandato" (
    "id" integer NOT NULL PRIMARY KEY,
    "parlamentar_id" integer NOT NULL REFERENCES "parlamentares_parlamentar" ("id"),
    "legislatura_id" integer NOT NULL REFERENCES "mesas_legislatura" ("id"),
    "partido_id" integer NOT NULL REFERENCES "parlamentares_partido" ("id"),
    "inicio_mandato" date NOT NULL,
    "fim_mandato" date NOT NULL,
    "is_afastado" bool NOT NULL,
    "suplencia" varchar(1) NOT NULL
)
;
COMMIT;
BEGIN;
CREATE TABLE "servicos_servico" (
    "id" integer NOT NULL PRIMARY KEY,
    "titulo" varchar(60) NOT NULL,
    "tipo" varchar(30) NOT NULL,
    "descricao" text NOT NULL,
    "data_inicio" date NULL,
    "data_fim" date NULL,
    "situacao" varchar(1) NOT NULL,
    "avaliacao" smallint unsigned NULL
)
;
COMMIT;
