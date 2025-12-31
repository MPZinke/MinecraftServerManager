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


import psycopg2.extras


from database.connect import connect
from database.classes import Biome, Location, World


@connect
def delete_location(cursor: psycopg2.extras.RealDictCursor, location_id: int) -> dict:
	query = """DELETE FROM "Locations" WHERE "id" = %s;"""
	cursor.execute(query, (location_id,))


@connect
def get_location(cursor: psycopg2.extras.RealDictCursor, location_id: int) -> list[Location]:
	query = """
		SELECT
			"Locations".*,
			"Biomes"."id" AS "Biomes.id",
			"Biomes"."world" AS "Biomes.world",
			"Biomes"."title" AS "Biomes.title",
			"Biomes"."description" AS "Biomes.description"
		FROM "Locations"
		LEFT JOIN "Biomes" ON "Locations"."Biomes.id" = "Biomes"."id"
		WHERE "Locations"."id" = %s;
	"""
	cursor.execute(query, (location_id,))
	location_dict: dict = cursor.fetchone()

	return Location.from_dict(
		id=location_dict["id"],
		title=location_dict["title"],
		location=location_dict["location"],
		notes=location_dict["notes"],
		world=None,
		biome=Biome(
			id=location_dict["Biomes.id"],
			world=location_dict["Biomes.world"],
			title=location_dict["Biomes.title"],
			description=location_dict["Biomes.description"],
		),
	)


@connect
def get_locations_for_world(cursor: psycopg2.extras.RealDictCursor, world: World) -> list[Location]:
	query = """
		SELECT
			"Locations".*,
			"Biomes"."id" AS "Biomes.id",
			"Biomes"."world" AS "Biomes.world",
			"Biomes"."title" AS "Biomes.title",
			"Biomes"."description" AS "Biomes.description"
		FROM "Locations"
		LEFT JOIN "Biomes" ON "Locations"."Biomes.id" = "Biomes"."id"
		WHERE "Worlds.id" = %s;
	"""
	cursor.execute(query, (world.id,))

	locations: list[Location] = []
	for location_dict in cursor:
		locations.append(
			Location.from_dict(
				id=location_dict["id"],
				title=location_dict["title"],
				location=location_dict["location"],
				notes=location_dict["notes"],
				world=world,
				biome=Biome(
					id=location_dict["Biomes.id"],
					world=location_dict["Biomes.world"],
					title=location_dict["Biomes.title"],
					description=location_dict["Biomes.description"],
				),
			)
		)
	return locations


@connect
def new_location(cursor: psycopg2.extras.RealDictCursor, location: World) -> None:
	query = """
		INSERT INTO "Locations" ("title", "location", "Worlds.id", "Biomes.id", "notes") VALUES
		(%s, %s, %s, %s, %s)
		RETURNING "id";
	"""
	cursor.execute(query, (location.title, location.location, location.world.id, location.biome.id, location.notes))

	location.id = cursor.fetchone()["id"]
