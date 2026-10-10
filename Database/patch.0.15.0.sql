

DROP TRIGGER DefaultWorldValues ON "Worlds";
DROP FUNCTION DefaultWorldValues;

CREATE TABLE "WorldsData"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"data" BYTEA DEFAULT ''::BYTEA,
	"index" INT NOT NULL,
	"Worlds.id" INT NOT NULL REFERENCES "Worlds"("id") ON DELETE CASCADE,
	UNIQUE ("index", "Worlds.id")
);


INSERT INTO "WorldsData" ("data", "index", "Worlds.id")
SELECT
	substring("Worlds"."data"::BYTEA FROM "Series"."start"::INT FOR 512000000) AS "data",
	("Series"."start" - 1) / 512000000 + 1 AS "index",
	"Worlds"."id"
FROM "Worlds"
CROSS JOIN LATERAL generate_series(
	1::BIGINT,
	octet_length("Worlds"."data")::BIGINT,
	512000000::BIGINT
) AS "Series"("start");


ALTER TABLE "Worlds" DROP COLUMN "data";


INSERT INTO "schema_versions" ("version", "notes") VALUES
(ARRAY[0, 15, 0]::INT[3], 'Adds data splitting');
