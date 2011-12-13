BEGIN;

-- retirando null de algumas colunas
ALTER TABLE "contatos_telefone" ALTER COLUMN nota DROP NOT NULL;
ALTER TABLE "contatos_telefone" ALTER COLUMN codigo_area DROP NOT NULL;

-- migrando dados de presidente da CasaLegislativa para Funcionarios
INSERT INTO casas_funcionario (casa_legislativa_id, cargo, setor, nome, nota, email)
  SELECT id, 'Presidente', 'presidencia', presidente, '', '' FROM casas_casalegislativa;

-- migrando dados de telefones da CasaLegislativa para model generic Telefone
INSERT INTO contatos_telefone (numero, tipo, content_type_id, object_id, codigo_area, nota)
  SELECT telefone, 'F', 12, id, '', '' FROM casas_casalegislativa;

-- deletando colunas fazer deois de estabilizar a versao
-- ALTER TABLE "casas_casalegislativa" DROP COLUMN presidente;
-- ALTER TABLE "casas_casalegislativa" DROP COLUMN telefone;
-- ALTER TABLE "contatos_telefone" DROP COLUMN codigo_area;
COMMIT;
