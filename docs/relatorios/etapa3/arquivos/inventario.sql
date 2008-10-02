BEGIN;
CREATE TABLE "inventario_bem" (
    "id" integer NOT NULL PRIMARY KEY,
    "casa_legislativa_id" integer NOT NULL,
    "equipamento_id" integer NOT NULL,
    "fornecedor_id" integer NOT NULL,
    "num_serie" varchar(50) NOT NULL UNIQUE,
    "num_tombamento" varchar(50) NOT NULL UNIQUE
)
;
CREATE TABLE "inventario_fabricante" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome" varchar(40) NOT NULL
)
;
CREATE TABLE "inventario_fornecedor" (
    "id" integer NOT NULL PRIMARY KEY,
    "nome" varchar(40) NOT NULL,
    "email" varchar(75) NOT NULL,
    "pagina_web" varchar(200) NOT NULL
)
;
CREATE TABLE "inventario_tipoequipamento" (
    "id" integer NOT NULL PRIMARY KEY,
    "tipo" varchar(40) NOT NULL
)
;
CREATE TABLE "inventario_equipamento" (
    "id" integer NOT NULL PRIMARY KEY,
    "fabricante_id" integer NOT NULL REFERENCES "inventario_fabricante" ("id"),
    "modelo_id" integer NOT NULL,
    UNIQUE ("fabricante_id", "modelo_id")
)
;
CREATE TABLE "inventario_modeloequipamento" (
    "id" integer NOT NULL PRIMARY KEY,
    "tipo_id" integer NOT NULL REFERENCES "inventario_tipoequipamento" ("id"),
    "modelo" varchar(30) NOT NULL
)
;
COMMIT;
