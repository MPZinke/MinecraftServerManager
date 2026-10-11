

CREATE TABLE "Worlds-DataChunks"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"chunk" BYTEA DEFAULT ''::BYTEA,
	"index" INT NOT NULL,
	"Worlds.id" INT NOT NULL REFERENCES "Worlds"("id") ON DELETE CASCADE,
	UNIQUE ("index", "Worlds.id")
);


INSERT INTO "Worlds-DataChunks" ("chunk", "index", "Worlds.id")
SELECT "data", "index", "Worlds.id"
FROM "WorldsData";


DROP TABLE "WorldsData";


INSERT INTO "schema_versions" ("version", "notes") VALUES
(ARRAY[0, 15, 1]::INT[3], 'Renames WorldsData. Uses key-values for DB query args.');
