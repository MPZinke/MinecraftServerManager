

DROP TABLE IF EXISTS "schema_versions";
CREATE TABLE "schema_versions"
(
	"version" INT[3] NOT NULL UNIQUE,
	"notes" TEXT NOT NULL,
	"applied" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


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
	"dimension" Dimension NOT NULL DEFAULT 'overworld',
	"title" TEXT NOT NULL UNIQUE,
	"description" TEXT
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
	"last_played" TIMESTAMP DEFAULT NULL,
	"name" VARCHAR(64) NOT NULL UNIQUE,
	"notes" TEXT NOT NULL DEFAULT '',
	"port" INT DEFAULT NULL,
	"seed" BIGINT DEFAULT NULL,
	"state" State NOT NULL DEFAULT 'offline',
	"Versions.id" INT NOT NULL REFERENCES "Versions"("id") ON DELETE CASCADE
);


DROP TABLE IF EXISTS "WorldsData" CASCADE;
CREATE TABLE "WorldsData"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"data" BYTEA DEFAULT ''::BYTEA,
	"Worlds.id" INT NOT NULL REFERENCES "Worlds"("id") ON DELETE CASCADE
);


CREATE UNIQUE INDEX ON "Worlds"("port")
  WHERE "port" IS NOT NULL;


-- ——————————————————————————————————————————————————— LOCATIONS  ——————————————————————————————————————————————————— --

DROP TABLE IF EXISTS "Locations" CASCADE;
CREATE TABLE "Locations"
(
	"id" SERIAL NOT NULL PRIMARY KEY,
	"title" TEXT NOT NULL,
	"location" INT[3] NOT NULL,
	"dimension" Dimension NOT NULL DEFAULT 'overworld',
	"favorited" TIMESTAMP DEFAULT NULL,  -- TODO: Add
	"Biomes.id" INT DEFAULT NULL REFERENCES "Biomes"("id") ON DELETE CASCADE,
	"Worlds.id" INT NOT NULL REFERENCES "Worlds"("id") ON DELETE CASCADE,
	"notes" TEXT NOT NULL DEFAULT ''
);
