

DROP TABLE IF EXISTS "Versions" CASCADE;
CREATE TABLE "Versions"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"is_deleted" BOOL NOT NULL DEFAULT FALSE,
	"released" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"tag" VARCHAR(48) NOT NULL UNIQUE,
	"title" VARCHAR(50) NOT NULL UNIQUE,
	"url" TEXT NOT NULL
);


DROP TYPE State CASCADE;
CREATE TYPE State AS ENUM (
	'offline',  -- Not building/starting and no docker container.
	'building', -- Building the docker image.
	'starting',  -- Image built, starting the docker container.
	'running',  -- Running the docker container.
	'exiting'  -- The docker container is paused.
);


DROP TABLE IF EXISTS "Worlds" CASCADE;
CREATE TABLE "Worlds"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"container_id" VARCHAR(64) DEFAULT NULL,
	"created" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"data" BYTEA DEFAULT NULL,
	"image_id" VARCHAR(64) DEFAULT NULL,
	"is_deleted" BOOL NOT NULL DEFAULT FALSE,
	"last_played" TIMESTAMP DEFAULT NULL,
	"port" INT DEFAULT NULL,
	"name" VARCHAR(64) NOT NULL UNIQUE,
	"notes" TEXT NOT NULL DEFAULT '',
	"state" State NOT NULL DEFAULT 'offline',
	"Versions.id" INT NOT NULL REFERENCES "Versions"("id") ON DELETE CASCADE
);


CREATE UNIQUE INDEX ON "Worlds"("port")
  WHERE "port" IS NOT NULL;


CREATE UNIQUE INDEX ON "Worlds"("container_id")
  WHERE "container_id" IS NOT NULL;


CREATE UNIQUE INDEX ON "Worlds"("image_id")
  WHERE "image_id" IS NOT NULL;


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
	"Worlds.id" INT NOT NULL REFERENCES "Worlds"("id") ON DELETE CASCADE,
	"Biomes.id" INT DEFAULT NULL REFERENCES "Biomes"("id"),
	"notes" TEXT NOT NULL DEFAULT ''
);


-- FROM: https://stackoverflow.com/a/42784814
CREATE OR REPLACE FUNCTION DefaultWorldValues()
RETURNS TRIGGER 
AS $$ BEGIN
	IF NEW."data" IS NULL THEN
		NEW."data" = '\x1f8b08000a6983660003ed913d0ec2300c463d730a9f20b55d3b4c1ca6432a217e844a22214e4f4aab32d12d2044def22d56fc39cf35501c22da9ae133fd94243ae50cb27a252fa6ac482ca40c68e5ab01a46bec865ce574b9efcf87f0762e8ff5fdca3bf31d4bfe08ae09e9d8b9788be576e4fff0aa2bfe5916ffd44af6df1a1b2095abf4e2cffd8ff677714861f3ed26954aa552f9240f1c92c349000a0000'::BYTEA;
	END IF;

	RETURN NEW;
END; 
$$ language plpgsql; 

CREATE TRIGGER DefaultWorldValues
BEFORE INSERT ON "Worlds"
FOR EACH ROW EXECUTE PROCEDURE DefaultWorldValues();
