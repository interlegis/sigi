BEGIN;
CREATE TABLE "servicos_servico" (
    "id" integer NOT NULL PRIMARY KEY,
    "tipo" varchar(50) NOT NULL,
    "descricao" text NOT NULL,
    "data_inicio" date NULL,
    "data_fim" date NULL,
    "situacao" varchar(1) NOT NULL,
    "avaliacao" smallint unsigned NULL
)
;
COMMIT;
