

DROP TABLE IF EXISTS "schema_versions";
CREATE TABLE "schema_versions"
(
	"version" INT[3] NOT NULL UNIQUE,
	"notes" TEXT NOT NULL,
	"applied" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO "schema_versions" ("version", "notes") VALUES
(ARRAY[0, 13, 0]::INT[3], 'Adds schema versioning');
