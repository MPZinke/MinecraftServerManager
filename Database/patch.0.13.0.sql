

CREATE TABLE IF NOT EXISTS "schema_versions"
(
	"version" INT[3] NOT NULL UNIQUE,
	"notes" TEXT NOT NULL,
	"applied" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO "schema_versions" ("version", "notes") 
SELECT "Temp"."version", "Temp"."notes"
FROM
(
	VALUES
	(ARRAY[0, 13, 0]::INT[3], 'Adds schema versioning')
) AS "Temp" ("version", "notes")
WHERE "Temp"."version" NOT IN (
	SELECT "version"
	FROM "schema_versions"
);
