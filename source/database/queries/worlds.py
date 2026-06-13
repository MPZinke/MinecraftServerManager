#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.26                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


import psycopg


from database.connect import connect
from database.classes import Version, World


@connect
async def delete_world(cursor: psycopg.AsyncCursor, world_id: int) -> dict:
	query = """DELETE FROM "Worlds" WHERE "id" = %s;"""
	await cursor.execute(query, (world_id,))


@connect
async def get_world(cursor: psycopg.AsyncCursor, world_id: int) -> dict:
	query = """
		SELECT
			"Worlds".*,
			"Versions"."id" AS "Versions.id",
			"Versions"."released" AS "Versions.released",
			"Versions"."tag" AS "Versions.tag",
			"Versions"."title" AS "Versions.title",
			"Versions"."url" AS "Versions.url"
		FROM "Worlds"
		JOIN "Versions" ON "Worlds"."Versions.id" = "Versions"."id"
		WHERE "Worlds"."id" = %s
		ORDER BY "Worlds"."id" ASC;
	"""
	await cursor.execute(query, (world_id,))

	world_dict = await cursor.fetchone()
	version = Version(
		id=world_dict["Versions.id"],
		released=world_dict["Versions.released"],
		tag=world_dict["Versions.tag"],
		title=world_dict["Versions.title"],
		url=world_dict["Versions.url"],
	)
	return World.from_dict(version=version, **world_dict)


@connect
async def get_world_info(cursor: psycopg.AsyncCursor, world_id: int) -> dict:
	query = """
		SELECT
			"Worlds"."id",
			"Worlds"."container_id",
			"Worlds"."created",
			NULL AS "data",
			"Worlds"."last_played",
			"Worlds"."name",
			"Worlds"."notes",
			"Worlds"."port",
			"Worlds"."seed",
			"Worlds"."state",
			"Versions"."id" AS "Versions.id",
			"Versions"."released" AS "Versions.released",
			"Versions"."tag" AS "Versions.tag",
			"Versions"."title" AS "Versions.title",
			"Versions"."url" AS "Versions.url"
		FROM "Worlds"
		JOIN "Versions" ON "Worlds"."Versions.id" = "Versions"."id"
		WHERE "Worlds"."id" = %s
		ORDER BY "Worlds"."id" ASC;
	"""
	await cursor.execute(query, (world_id,))

	world_dict = await cursor.fetchone()
	version = Version(
		id=world_dict["Versions.id"],
		released=world_dict["Versions.released"],
		tag=world_dict["Versions.tag"],
		title=world_dict["Versions.title"],
		url=world_dict["Versions.url"],
	)
	return World.from_dict(version=version, **world_dict)


@connect
async def get_worlds_info(cursor: psycopg.AsyncCursor) -> list[World]:
	query = """
		SELECT
			"Worlds"."id",
			"Worlds"."container_id",
			"Worlds"."created",
			NULL AS "data",
			"Worlds"."last_played",
			"Worlds"."name",
			"Worlds"."notes",
			"Worlds"."port",
			"Worlds"."seed",
			"Worlds"."state",
			"Versions"."id" AS "Versions.id",
			"Versions"."released" AS "Versions.released",
			"Versions"."tag" AS "Versions.tag",
			"Versions"."title" AS "Versions.title",
			"Versions"."url" AS "Versions.url"
		FROM "Worlds"
		JOIN "Versions" ON "Worlds"."Versions.id" = "Versions"."id"
		ORDER BY "Worlds"."id" ASC;
	"""
	await cursor.execute(query)

	worlds: list[World] = []
	async for world_dict in cursor:
		version = Version(
			id=world_dict["Versions.id"],
			released=world_dict["Versions.released"],
			tag=world_dict["Versions.tag"],
			title=world_dict["Versions.title"],
			url=world_dict["Versions.url"],
		)
		worlds.append(World.from_dict(version=version, **world_dict))

	return worlds


@connect
async def get_running_worlds_info(cursor: psycopg.AsyncCursor) -> list[World]:
	query = """
		SELECT
			"Worlds"."id",
			"Worlds"."container_id",
			"Worlds"."created",
			NULL AS "data",
			"Worlds"."last_played",
			"Worlds"."name",
			"Worlds"."notes",
			"Worlds"."port",
			"Worlds"."seed",
			"Worlds"."state",
			"Versions"."id" AS "Versions.id",
			"Versions"."released" AS "Versions.released",
			"Versions"."tag" AS "Versions.tag",
			"Versions"."title" AS "Versions.title",
			"Versions"."url" AS "Versions.url"
		FROM "Worlds"
		JOIN "Versions" ON "Worlds"."Versions.id" = "Versions"."id"
		WHERE "Worlds"."state" = 'running'
		ORDER BY "Worlds"."id" ASC;
	"""
	await cursor.execute(query)

	worlds: list[World] = []
	async for world_dict in cursor:
		version = Version(
			id=world_dict["Versions.id"],
			released=world_dict["Versions.released"],
			tag=world_dict["Versions.tag"],
			title=world_dict["Versions.title"],
			url=world_dict["Versions.url"],
		)
		worlds.append(World.from_dict(version=version, **world_dict))

	return worlds


@connect
async def new_world(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		INSERT INTO "Worlds" ("name", "data", "notes", "Versions.id") VALUES
		(%s, %s, %s, %s)
		RETURNING "id";
	"""
	await cursor.execute(query, (world.name, world.data, world.notes, world.version.id))

	world.id = (await cursor.fetchone())["id"]


@connect
async def set_world_container(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "container_id" = %s, "port" = %s
		WHERE "id" = %s;
	"""
	await cursor.execute(query, (world.container_id, world.port, world.id))


@connect
async def set_world_stopping(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "state" = 'stopping'
		WHERE "id" = %s;
	"""
	await cursor.execute(query, (world.id,))

	world.state = "stopping"


@connect
async def set_world_port(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "port" = %s
		WHERE "id" = %s;
	"""
	await cursor.execute(query, (world.port, world.id))


@connect
async def set_world_running(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "container_id" = %s, "last_played" = NOW(), "port" = %s, "state" = 'running'
		WHERE "id" = %s;
	"""
	await cursor.execute(query, (world.container_id, world.port, world.id))


@connect
async def set_world_starting(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "state" = 'starting'
		WHERE "id" = %s;
	"""
	await cursor.execute(query, (world.id,))

	world.state = "starting"


@connect
async def set_world_seed(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "seed" = %s
		WHERE "id" = %s;
	"""
	await cursor.execute(query, (world.seed, world.id))


@connect
async def set_world_state(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "state" = %s
		WHERE "id" = %s;
	"""
	await cursor.execute(query, (world.state, world.id))


@connect
async def set_world_offline(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "container_id" = NULL, "data" = %s, "port" = NULL, "state" = 'offline'
		WHERE "id" = %s;
	"""
	await cursor.execute(query, (world.data, world.id))

	world.port = None
	world.state = "offline"
