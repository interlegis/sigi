BEGIN;

-- deletando colunas da CasaLegislativa
ALTER TABLE "diagnosticos_diagnostico" ADD COLUMN "responsavel_id" integer NOT NULL REFERENCES "servidores_servidor" ("id");
ALTER TABLE "diagnosticos_equipe" DROP COLUMN "is_chefe";

COMMIT;
