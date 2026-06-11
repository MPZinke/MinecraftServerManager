#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.29                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


import psycopg


from database.connect import connect
from database.classes import Biome, Location, World


@connect
async def delete_location(cursor: psycopg.AsyncCursor, location_id: int) -> dict:
	query = """DELETE FROM "Locations" WHERE "id" = %s;"""
	await cursor.execute(query, (location_id,))


@connect
async def get_location(cursor: psycopg.AsyncCursor, location_id: int) -> list[Location]:
	query = """
		SELECT
			"Locations".*,
			"Biomes"."id" AS "Biomes.id",
			"Biomes"."dimension" AS "Biomes.dimension",
			"Biomes"."title" AS "Biomes.title",
			"Biomes"."description" AS "Biomes.description"
		FROM "Locations"
		LEFT JOIN "Biomes" ON "Locations"."Biomes.id" = "Biomes"."id"
		WHERE "Locations"."id" = %s;
	"""
	await cursor.execute(query, (location_id,))
	location_dict: dict = await cursor.fetchone()

	biome = Biome(
		id=location_dict["Biomes.id"],
		dimension=location_dict["Biomes.dimension"],
		title=location_dict["Biomes.title"],
		description=location_dict["Biomes.description"],
	)

	return Location.from_dict(world=None, biome=biome, **location_dict,)


@connect
async def get_locations_for_world(cursor: psycopg.AsyncCursor, world: World) -> list[Location]:
	query = """
		SELECT
			"Locations".*,
			"Biomes"."id" AS "Biomes.id",
			"Biomes"."dimension" AS "Biomes.dimension",
			"Biomes"."title" AS "Biomes.title",
			"Biomes"."description" AS "Biomes.description"
		FROM "Locations"
		LEFT JOIN "Biomes" ON "Locations"."Biomes.id" = "Biomes"."id"
		WHERE "Worlds.id" = %s;
	"""
	await cursor.execute(query, (world.id,))

	locations: list[Location] = []
	async for location_dict in cursor:
		biome = Biome(
			id=location_dict["Biomes.id"],
			dimension=location_dict["Biomes.dimension"],
			title=location_dict["Biomes.title"],
			description=location_dict["Biomes.description"],
		)
		locations.append(Location.from_dict(world=world, biome=biome, **location_dict))
	return locations


@connect
async def new_location(cursor: psycopg.AsyncCursor, location: World) -> None:
	query = """
		INSERT INTO "Locations" ("title", "dimension", "location", "Worlds.id", "Biomes.id", "notes") VALUES
		(%s, %s, %s, %s, %s, %s)
		RETURNING "id";
	"""
	await cursor.execute(
		query,
		(location.title, location.dimension, location.location, location.world.id, location.biome.id, location.notes),
	)

	location.id = (await cursor.fetchone())["id"]
