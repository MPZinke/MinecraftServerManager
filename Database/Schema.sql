
-- ———————————————————————————————————————————————————— VERSIONS ———————————————————————————————————————————————————— --

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


-- ————————————————————————————————————————————————————— WORLDS ————————————————————————————————————————————————————— --

DROP TYPE State CASCADE;
CREATE TYPE State AS ENUM (
	'offline',  -- Not building/starting and no docker container.
	'starting',  -- Image built, starting the docker container.
	'running',  -- Running the docker container.
	'exiting'  -- The docker container is paused.
);


DROP TABLE IF EXISTS "Worlds" CASCADE;
CREATE TABLE "Worlds"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"created" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"data" BYTEA DEFAULT NULL,
	"is_deleted" BOOL NOT NULL DEFAULT FALSE,
	"last_played" TIMESTAMP DEFAULT NULL,
	"name" VARCHAR(64) NOT NULL UNIQUE,
	"notes" TEXT NOT NULL DEFAULT '',
	"port" INT DEFAULT NULL,
	"state" State NOT NULL DEFAULT 'offline',
	"Versions.id" INT NOT NULL REFERENCES "Versions"("id") ON DELETE CASCADE
);


CREATE UNIQUE INDEX ON "Worlds"("port")
  WHERE "port" IS NOT NULL;


-- FROM: https://stackoverflow.com/a/42784814
CREATE OR REPLACE FUNCTION DefaultWorldValues()
RETURNS TRIGGER
AS $$ BEGIN
	IF NEW."data" IS NULL THEN
		NEW."data" = '\x1f8b080070e5516902ffedd1310ec2301004c0ab79052f889cc840c56352b8a30ab694e763a541a227529499664fdb6c71a5bde6a1ae35fe2875f79cb7ec7e33a571fade5bffc8d32dae2976d0de755efa649c53e9ff7fd6a5954b00000000000000000070201ff03316c500280000'::BYTEA;
	END IF;

	RETURN NEW;
END;
$$ language plpgsql;

CREATE TRIGGER DefaultWorldValues
BEFORE INSERT ON "Worlds"
FOR EACH ROW EXECUTE PROCEDURE DefaultWorldValues();


-- ————————————————————————————————————————————————————— BIOMES ————————————————————————————————————————————————————— --

DROP TYPE World CASCADE;
CREATE TYPE World AS ENUM (
	'Overworld',
	'Nether',
	'End'
);


DROP TABLE IF EXISTS "Biomes" CASCADE;
CREATE TABLE "Biomes"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"world" World NOT NULL,
	"title" TEXT NOT NULL UNIQUE,
	"description" TEXT
);


-- ——————————————————————————————————————————————————— LOCATIONS  ——————————————————————————————————————————————————— --

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
