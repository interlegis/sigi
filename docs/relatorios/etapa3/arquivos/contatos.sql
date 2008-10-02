BEGIN;
CREATE TABLE "contatos_unidadefederativa" (
    "codigo_ibge" integer unsigned NOT NULL PRIMARY KEY,
    "nome" varchar(25) NOT NULL,
    "sigla" varchar(2) NOT NULL,
    "regiao" varchar(2) NOT NULL,
    "populacao" integer unsigned NOT NULL
)
;
CREATE TABLE "contatos_telefone" (
    "id" integer NOT NULL PRIMARY KEY,
    "codigo_ddd" varchar(2) NOT NULL,
    "numero" varchar(9) NOT NULL,
    "tipo" varchar(1) NOT NULL,
    "nota" varchar(70) NOT NULL,
    "content_type_id" integer NOT NULL,
    "object_id" integer unsigned NOT NULL,
    UNIQUE ("codigo_ddd", "numero", "tipo")
)
;
CREATE TABLE "contatos_municipio" (
    "codigo_ibge" integer unsigned NOT NULL PRIMARY KEY,
    "codigo_mesorregiao" integer unsigned NOT NULL,
    "codigo_microrregiao" integer unsigned NOT NULL,
    "nome" varchar(50) NOT NULL,
    "uf_id" integer NOT NULL REFERENCES "contatos_unidadefederativa"
        ("codigo_ibge"),
    "is_capital" bool NOT NULL,
    "populacao" integer unsigned NOT NULL,
    "is_polo" bool NOT NULL,
    "latitude" decimal NULL,
    "longitude" decimal NULL
)
;
CREATE TABLE "contatos_contato" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome" varchar(60) NOT NULL,
    "nota" varchar(70) NOT NULL,
    "email" varchar(75) NOT NULL,
    "municipio_id" integer NULL REFERENCES "contatos_municipio"
        ("codigo_ibge"),
    "content_type_id" integer NOT NULL,
    "object_id" integer unsigned NOT NULL
)
;
COMMIT;
