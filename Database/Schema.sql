
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


-- ———————————————————————————————————————————————————— PLAYERS  ———————————————————————————————————————————————————— --

DROP TABLE IF EXISTS "Players" CASCADE;
CREATE TABLE "Players"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"uuid" UUID NOT NULL,
	"name" VARCHAR(50) NOT NULL UNIQUE
);


-- ————————————————————————————————————————————————————— WORLDS ————————————————————————————————————————————————————— --

DROP TYPE State CASCADE;
CREATE TYPE State AS ENUM (
	'offline',  -- Not building/starting and no docker container.
	'starting',  -- Image built, starting the docker container.
	'running',  -- Running the docker container.
	'stopping'  -- The docker container as shutting down.
);


DROP TABLE IF EXISTS "Worlds" CASCADE;
CREATE TABLE "Worlds"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"container_id" CHAR(64) DEFAULT NULL,
	"created" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"data" BYTEA DEFAULT NULL,
	"last_played" TIMESTAMP DEFAULT NULL,
	"name" VARCHAR(64) NOT NULL UNIQUE,
	"notes" TEXT NOT NULL DEFAULT '',
	"port" INT DEFAULT NULL,
	"seed" BIGINT DEFAULT NULL,
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

DROP TYPE Dimension CASCADE;
CREATE TYPE Dimension AS ENUM (
	'overworld',
	'the_nether',
	'the_end'
);


DROP TABLE IF EXISTS "Biomes" CASCADE;
CREATE TABLE "Biomes"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"dimension" Dimension NOT NULL,
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
	"dimension" Dimension NOT NULL DEFAULT 'overworld',
	"Biomes.id" INT DEFAULT NULL REFERENCES "Biomes"("id") ON DELETE CASCADE,
	"Worlds.id" INT NOT NULL REFERENCES "Worlds"("id") ON DELETE CASCADE,
	"notes" TEXT NOT NULL DEFAULT ''
);
