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


from typing import Awaitable


import psycopg


from database.connect import connect
from database.classes import Version, World


@connect
async def delete_world(cursor: psycopg.AsyncCursor, id: int) -> dict:
	query = """DELETE FROM "Worlds" WHERE "id" = %(id)s;"""
	await cursor.execute(query, {"id": id})


@connect
async def get_world(cursor: psycopg.AsyncCursor, id: int) -> dict:
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
		WHERE "Worlds"."id" = %(id)s
		ORDER BY "Worlds"."id" ASC;
	"""
	await cursor.execute(query, {"id": id})

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
async def get_worlds(cursor: psycopg.AsyncCursor) -> list[World]:
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
async def get_world_data(cursor: psycopg.AsyncCursor, id: int) -> dict:
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
		WHERE "Worlds"."id" = %(id)s
		ORDER BY "Worlds"."id" ASC;
	"""
	await cursor.execute(query, {"id": id})

	world_dict = await cursor.fetchone()
	version = Version(
		id=world_dict["Versions.id"],
		released=world_dict["Versions.released"],
		tag=world_dict["Versions.tag"],
		title=world_dict["Versions.title"],
		url=world_dict["Versions.url"],
	)

	query = """
		SELECT *
		FROM "Worlds-DataChunks"
		WHERE "Worlds.id" = %(id)s
		ORDER BY "index";
	"""
	await cursor.execute(query, {"id": id})
	data = b"".join([world_chunk_dict["chunk"] async for world_chunk_dict in cursor])

	return World.from_dict(data=data, version=version, **world_dict)


@connect
async def get_running_worlds(cursor: psycopg.AsyncCursor) -> list[World]:
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
		INSERT INTO "Worlds" ("name", "notes", "Versions.id") VALUES
		(%(name)s, %(notes)s, %(Versions.id)s)
		RETURNING "id";
	"""
	await cursor.execute(query, {"name": world.name, "notes": world.notes, "Versions.id": world.version.id})

	world.id = (await cursor.fetchone())["id"]

	chunks: list[bytes] = []
	for x in range(len(world.data) // 512_000_000 + 1):
		chunks.append(world.data[512_000_000 * x : 512_000_000 * (x + 1)])

	query = """
		INSERT INTO "Worlds-DataChunks" ("chunk", "index", "Worlds.id")
		SELECT "Temp"."chunk", "Temp"."index", %(Worlds.id)s
		FROM UNNEST(
			%(chunks)s::BYTEA[],
			%(indexes)s::INT[]
		) AS "Temp"("chunk", "index");
	"""
	await cursor.execute(query, {"Worlds.id": world.id, "chunks": chunks, "indexes": [x+1 for x in range(len(chunks))]})


@connect
async def set_name(cursor: psycopg.AsyncCursor, id: int, name: str) -> None:
	query = """
		UPDATE "Worlds"
		SET "name" = %(name)s
		WHERE "id" = %(id)s;
	"""
	await cursor.execute(query, {"id": id, "name": name})


@connect
async def set_world_container(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "container_id" = %(container_id)s, "port" = %(port)s
		WHERE "id" = %(id)s;
	"""
	await cursor.execute(query, {"container_id": world.container_id, "port": world.port, "id": world.id})


@connect
async def set_world_stopping(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "state" = 'stopping'
		WHERE "id" = %(id)s;
	"""
	await cursor.execute(query, {"id": world.id})

	world.state = "stopping"


@connect
async def set_world_port(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "port" = %(port)s
		WHERE "id" = %(id)s;
	"""
	await cursor.execute(query, {"port": world.port, "id": world.id})


@connect
async def set_world_running(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "container_id" = %(container_id)s, "last_played" = NOW(), "port" = %(port)s, "state" = 'running'
		WHERE "id" = %(id)s;
	"""
	await cursor.execute(query, {"container_id": world.container_id, "port": world.port, "id": world.id})


@connect
async def set_world_starting(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "state" = 'starting'
		WHERE "id" = %(id)s;
	"""
	await cursor.execute(query, {"id": world.id})

	world.state = "starting"


@connect
async def set_world_seed(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "seed" = %(seed)s
		WHERE "id" = %(id)s;
	"""
	await cursor.execute(query, {"seed": world.seed, "id": world.id})


@connect
async def set_world_state(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "state" = %(state)s
		WHERE "id" = %(id)s;
	"""
	await cursor.execute(query, {"state": world.state, "id": world.id})


@connect
async def set_world_offline(cursor: psycopg.AsyncCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "container_id" = NULL, "port" = NULL, "state" = 'offline'
		WHERE "id" = %(id)s;
	"""
	query_promise: Awaitable = cursor.execute(query, {"id": world.id})

	world.port = None
	world.state = "offline"

	chunks: list[bytes] = []
	for x in range(len(world.data) // 512_000_000 + 1):
		chunks.append(world.data[512_000_000 * x : 512_000_000 * (x + 1)])

	await query_promise

	# FROM: https://stackoverflow.com/a/18799497
	# ASSUMPTION: The size of a world will never decrease. Therefore we will not worry about emptying world chunk rows.
	query = """
		UPDATE "Worlds-DataChunks"
		SET "chunk" = "Temp"."chunk"
		FROM UNNEST(
			%(chunks)s::BYTEA[],
			%(indexes)s::INT[]
		) AS "Temp" ("chunk", "index")
		WHERE "Worlds.id" = %(Worlds.id)s
		  AND "Worlds-DataChunks"."index" = "Temp"."index"
		RETURNING "id";
	"""
	await cursor.execute(query, {"chunks": chunks, "indexes": list(range(1, len(chunks)+1)), "Worlds.id": world.id})
	number_of_updated_chunks: int = len([world_chunk_dict async for world_chunk_dict in cursor])

	# Insert any chunk that were not preexisting.
	if(number_of_updated_chunks < len(chunks)):
		query = """
			INSERT INTO "Worlds-DataChunks" ("chunk", "index", "Worlds.id")
			SELECT "Temp"."chunk", "Temp"."index", %(Worlds.id)s
			FROM UNNEST(
				%(chunks)s::BYTEA[],
				%(indexes)s::INT[]
			) AS "Temp" ("chunk", "index");
		"""

		remaining_chunks: list[bytes] = chunks[number_of_updated_chunks:]
		remaining_indexes: list[int] = list(range(number_of_updated_chunks+1, len(chunks)+1))
		await cursor.execute(query, {"Worlds.id": world.id, "chunks": remaining_chunks, "indexes": remaining_indexes})
