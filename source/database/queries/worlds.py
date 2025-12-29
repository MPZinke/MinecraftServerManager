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


import psycopg2.extras


from database.connect import connect
from database.classes import Version, World


@connect
def delete_world(cursor: psycopg2.extras.RealDictCursor, world_id: int) -> dict:
	query = """DELETE FROM "Worlds" WHERE "id" = %s;"""
	cursor.execute(query, (world_id,))


@connect
def get_world(cursor: psycopg2.extras.RealDictCursor, world_id: int) -> dict:
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

	cursor.execute(query, (world_id,))
	world_dict = cursor.fetchone()
	version = Version(
		id=world_dict["Versions.id"],
		released=world_dict["Versions.released"],
		tag=world_dict["Versions.tag"],
		title=world_dict["Versions.title"],
		url=world_dict["Versions.url"],
	)
	return World.from_dict(version=version, **world_dict)


@connect
def get_worlds(cursor: psycopg2.extras.RealDictCursor) -> list[World]:
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
	worlds: list[World] = []

	cursor.execute(query)
	for world_dict in cursor:
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
def get_running_worlds(cursor: psycopg2.extras.RealDictCursor) -> list[World]:
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
	worlds: list[World] = []

	cursor.execute(query)
	for world_dict in cursor:
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
def new_world(cursor: psycopg2.extras.RealDictCursor, world: World) -> None:
	query = """
		INSERT INTO "Worlds" ("name", "data", "notes", "Versions.id") VALUES
		(%s, %s, %s, %s)
		RETURNING "id";
	"""

	cursor.execute(query, (world.name, world.data, world.notes, world.version.id))
	world.id = cursor.fetchone()["id"]


@connect
def set_world_exiting(cursor: psycopg2.extras.RealDictCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "state" = 'exiting'
		WHERE "id" = %s
		RETURNING *;
	"""

	cursor.execute(query, (world.id,))
	world.state = "exiting"


@connect
def set_world_port(cursor: psycopg2.extras.RealDictCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "port" = %s
		WHERE "id" = %s
		RETURNING *;
	"""

	cursor.execute(query, (world.port, world.id))


@connect
def set_world_running(cursor: psycopg2.extras.RealDictCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "last_played" = NOW(), "port" = %s, "state" = 'running'
		WHERE "id" = %s
		RETURNING *;
	"""

	cursor.execute(query, (world.port, world.id))


@connect
def set_world_starting(cursor: psycopg2.extras.RealDictCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "state" = 'starting'
		WHERE "id" = %s
		RETURNING *;
	"""

	cursor.execute(query, (world.id,))
	world.state = "starting"


@connect
def set_world_state(cursor: psycopg2.extras.RealDictCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "state" = %s
		WHERE "id" = %s
		RETURNING *;
	"""

	cursor.execute(query, (world.state, world.id))


@connect
def set_world_stopped(cursor: psycopg2.extras.RealDictCursor, world: World) -> None:
	query = """
		UPDATE "Worlds"
		SET "data" = %s, "port" = NULL, "state" = 'offline'
		WHERE "id" = %s
		RETURNING *;
	"""

	cursor.execute(query, (world.data, world.id))
	world.port = None
	world.state = "offline"
