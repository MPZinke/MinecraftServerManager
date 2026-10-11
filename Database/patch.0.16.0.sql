

ALTER TABLE "Players" ADD CONSTRAINT UNIQUE ("uuid");


INSERT INTO "schema_versions" ("version", "notes") VALUES
(ARRAY[0, 16, 0]::INT[3], 'Enables new, unique players.');
