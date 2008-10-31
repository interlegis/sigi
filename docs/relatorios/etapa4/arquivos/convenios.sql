BEGIN;
CREATE TABLE "convenios_anexo" (
    "id" integer NOT NULL PRIMARY KEY,
    "convenio_id" integer NOT NULL,
    "arquivo" varchar(100) NOT NULL,
    "descricao" varchar(70) NOT NULL,
    "data_pub" date NOT NULL
)
;
CREATE TABLE "convenios_convenio" (
    "id" integer NOT NULL PRIMARY KEY,
    "casa_legislativa_id" integer NOT NULL,
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
    "equipamento_id" integer NOT NULL,
    "quantidade" smallint unsigned NOT NULL
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
