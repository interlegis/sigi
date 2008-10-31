BEGIN;
CREATE TABLE "casas_casalegislativa" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome" varchar(60) NOT NULL,
    "sigla" varchar(30) NOT NULL,
    "tipo" varchar(2) NOT NULL,
    "cnpj" varchar(18) NOT NULL,
    "logradouro" varchar(100) NOT NULL,
    "bairro" varchar(40) NOT NULL,
    "cidade_id" integer NOT NULL,
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
