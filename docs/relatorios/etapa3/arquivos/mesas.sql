BEGIN;
CREATE TABLE "mesas_membromesadiretora" (
    "id" integer NOT NULL PRIMARY KEY,
    "parlamentar_id" integer NOT NULL,
    "cargo_id" integer NOT NULL,
    "mesa_diretora_id" integer NOT NULL
)
;
CREATE TABLE "mesas_cargo" (
    "id" integer NOT NULL PRIMARY KEY,
    "descricao" varchar(30) NOT NULL
)
;
CREATE TABLE "mesas_coligacao" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome" varchar(50) NOT NULL,
    "legislatura_id" integer NOT NULL,
    "numero_votos" integer unsigned NULL
)
;
CREATE TABLE "mesas_legislatura" (
    "id" integer NOT NULL PRIMARY KEY,
    "numero" smallint unsigned NOT NULL,
    "data_inicio" date NOT NULL,
    "data_fim" date NOT NULL,
    "data_eleicao" date NOT NULL
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
    "casa_legislativa_id" integer NOT NULL
)
;
CREATE TABLE "mesas_composicaocoligacao" (
    "id" integer NOT NULL PRIMARY KEY,
    "coligacao_id" integer NOT NULL REFERENCES "mesas_coligacao" ("id"),
    "partido_id" integer NOT NULL
)
;
COMMIT;
