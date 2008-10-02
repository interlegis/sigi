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
    "cidade_id" integer NOT NULL,
    "cep" varchar(9) NOT NULL,
    "pagina_web" varchar(200) NOT NULL,
    "email" varchar(75) NOT NULL
)
;
CREATE TABLE "parlamentares_mandato" (
    "id" integer NOT NULL PRIMARY KEY,
    "parlamentar_id" integer NOT NULL REFERENCES
        "parlamentares_parlamentar" ("id"),
    "legislatura_id" integer NOT NULL,
    "partido_id" integer NOT NULL REFERENCES "parlamentares_partido" ("id"),
    "inicio_mandato" date NOT NULL,
    "fim_mandato" date NOT NULL,
    "is_afastado" bool NOT NULL,
    "suplencia" varchar(1) NOT NULL
)
;
COMMIT;
