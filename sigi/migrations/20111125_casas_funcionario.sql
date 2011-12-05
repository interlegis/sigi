BEGIN;

-- criando tabela do model Funcionario e Presidente
CREATE TABLE "casas_funcionario" (
    "id" serial NOT NULL PRIMARY KEY,
    "casa_legislativa_id" integer NOT NULL REFERENCES "casas_casalegislativa" ("id") DEFERRABLE INITIALLY DEFERRED,
    "nome" varchar(100) NOT NULL,
    "nota" varchar(70) NOT NULL,
    "email" varchar(75) NOT NULL,
    "cargo" varchar(100),
    "funcao" varchar(100),
    "setor" varchar(100),
    "tempo_de_servico" varchar(50)
);
CREATE INDEX "casas_funcionario_casa_legislativa_id" ON "casas_funcionario" ("casa_legislativa_id");

-- migrando dados de presidente da CasaLegislativa para Funcionarios
INSERT INTO casas_funcionario (casa_legislativa_id, cargo, nome, nota, email)
  SELECT id, 'Presidente', presidente, '', '' FROM casas_casalegislativa;

-- migrando dados de telefones da CasaLegislativa para model generic Telefone
INSERT INTO contatos_telefone (numero, tipo, content_type_id, object_id, codigo_area, nota)
  SELECT telefone, 'F', 12, id, '', '' FROM casas_casalegislativa;

-- deletando colunas da CasaLegislativa
ALTER TABLE "casas_casalegislativa" DROP COLUMN presidente;
ALTER TABLE "casas_casalegislativa" DROP COLUMN telefone;

-- retirando null de algumas colunas
ALTER TABLE "contatos_telefone" ALTER COLUMN codigo_area DROP NOT NULL;
ALTER TABLE "contatos_telefone" ALTER COLUMN codigo_nota DROP NOT NULL;
COMMIT;
