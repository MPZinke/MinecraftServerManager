

DROP TABLE IF EXISTS "Versions" CASCADE;
DROP TABLE IF EXISTS "Worlds" CASCADE;
DROP TABLE IF EXISTS "Biomes" CASCADE;
DROP TABLE IF EXISTS "Locations" CASCADE;


CREATE TABLE "Versions"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"released" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"tag" VARCHAR(48) NOT NULL UNIQUE,
	"title" VARCHAR(50) NOT NULL UNIQUE,
	"url" TEXT NOT NULL
);


CREATE TABLE "Worlds"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"created" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"name" VARCHAR(64) NOT NULL UNIQUE,
	"notes" TEXT NOT NULL DEFAULT '',

	"last_played" TIMESTAMP DEFAULT NULL,
	"container_id" VARCHAR(12) NOT NULL DEFAULT '',
	"container_name" VARCHAR(64) NOT NULL UNIQUE,
	"image_tag" VARCHAR(64) NOT NULL UNIQUE,
	"is_running" BOOL DEFAULT FALSE,
	"mapped_port" INT DEFAULT NULL,

	"data" BYTEA NOT NULL,
	"Versions.id" INT NOT NULL,
	FOREIGN KEY("Versions.id") REFERENCES "Versions"("id")
);


CREATE UNIQUE INDEX ON "Worlds"("mapped_port")
  WHERE "mapped_port" IS NOT NULL;


DROP TABLE IF EXISTS "Biomes" CASCADE;
CREATE TABLE "Biomes"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"title" TEXT NOT NULL UNIQUE
);


DROP TABLE IF EXISTS "Locations" CASCADE;
CREATE TABLE "Locations"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"title" TEXT NOT NULL,
	"location" INT[3] NOT NULL,
	"Worlds.id" INT NOT NULL,
	FOREIGN KEY("Worlds.id") REFERENCES "Worlds"("id"),
	"Biomes.id" INT DEFAULT NULL,
	FOREIGN KEY("Biomes.id") REFERENCES "Biomes"("id"),
	"notes" TEXT NOT NULL DEFAULT ''
);


-- FROM: https://stackoverflow.com/a/42784814
CREATE OR REPLACE FUNCTION DefaultWorldValues()
RETURNS TRIGGER 
AS $$ BEGIN
	IF NEW."data" IS NULL THEN
		NEW."data" = '\x1f8b08000a6983660003ed913d0ec2300c463d730a9f20b55d3b4c1ca6432a217e844a22214e4f4aab32d12d2044def22d56fc39cf35501c22da9ae133fd94243ae50cb27a252fa6ac482ca40c68e5ab01a46bec865ce574b9efcf87f0762e8ff5fdca3bf31d4bfe08ae09e9d8b9788be576e4fff0aa2bfe5916ffd44af6df1a1b2095abf4e2cffd8ff677714861f3ed26954aa552f9240f1c92c349000a0000'::BYTEA;
	END IF;

	IF NEW."Versions.id" IS NULL THEN
		NEW."Versions.id" = (SELECT "id" FROM "Versions" ORDER BY "released" DESC LIMIT 1);
	END IF;

	IF NEW."image_tag" IS NULL THEN
		NEW."image_tag" = 'minecraft:' || (SELECT "tag" FROM "Versions" WHERE "id" = NEW."Versions.id") || '-' || NEW."id";
	END IF;

	IF NEW."container_name" IS NULL THEN
		NEW."container_name" = 'minecraft_' || (SELECT "tag" FROM "Versions" WHERE "id" = NEW."Versions.id") || '-' || NEW."id";
	END IF;

	RETURN NEW;
END; 
$$ language plpgsql; 

CREATE TRIGGER DefaultWorldValues
BEFORE INSERT ON "Worlds"
FOR EACH ROW EXECUTE PROCEDURE DefaultWorldValues();
