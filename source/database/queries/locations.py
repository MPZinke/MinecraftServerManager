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
	query = """DELETE FROM "Locations" WHERE "id" = %(id)s;"""
	await cursor.execute(query, {"id": location_id})


@connect
async def favorite_location(cursor: psycopg.AsyncCursor, location_id: int) -> dict:
	query = """UPDATE "Locations" SET "favorited" = CURRENT_TIMESTAMP WHERE "id" = %(id)s;"""
	await cursor.execute(query, {"id": location_id})


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
		WHERE "Locations"."id" = %(id)s;
	"""
	await cursor.execute(query, {"id": location_id})
	location_dict: dict = await cursor.fetchone_or_fail()

	if(location_dict["Biomes.id"] is None):
		biome = None

	else:
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
		WHERE "Worlds.id" = %(Worlds.id)s
		ORDER BY "favorited" ASC NULLS LAST, "title" ASC;
	"""
	await cursor.execute(query, {"Worlds.id": world.id})

	locations: list[Location] = []
	async for location_dict in cursor:
		if(location_dict["Biomes.id"] is None):
			biome = None

		else:
			biome = Biome(
				id=location_dict["Biomes.id"],
				dimension=location_dict["Biomes.dimension"],
				title=location_dict["Biomes.title"],
				description=location_dict["Biomes.description"],
			)
		locations.append(Location.from_dict(world=world, biome=biome, **location_dict))
	return locations


@connect
async def new_location(cursor: psycopg.AsyncCursor, location: Location) -> None:
	query = """
		INSERT INTO "Locations" ("title", "dimension", "location", "Worlds.id", "Biomes.id", "notes") VALUES
		(%(title)s, %(dimension)s, %(location)s, %(Worlds.id)s, %(Biomes.id)s, %(notes)s)
		RETURNING "id";
	"""
	await cursor.execute(
		query,
		{
			"title": location.title,
			"dimension": location.dimension,
			"location": location.location,
			"World.id": location.world.id,
			"Biome.id": location.biome.id,
			"notes": location.notes,
		},
	)

	location.id = (await cursor.fetchone())["id"]


@connect
async def new_locations(cursor: psycopg.AsyncCursor, locations: list[Location]) -> None:
	if(len(locations) == 0):
		return

	query = """
		INSERT INTO "Locations" ("title", "dimension", "location", "Worlds.id", "Biomes.id", "notes")
		SELECT
			"Temp"."title",
			"Temp"."dimension",
			ARRAY[
				"Temp"."location_x",
				"Temp"."location_y",
				"Temp"."location_z"
			]::INTEGER[3],
			%(Worlds.id)s,
			"Temp"."Biomes.id",
			"Temp"."notes"
		FROM UNNEST(
			%(titles)s::TEXT[], -- "title"
			%(dimensions)s::Dimension[], -- "dimension"
			%(locations_x)s::INTEGER[], -- "location[0]"
			%(locations_y)s::INTEGER[], -- "location[1]"
			%(locations_z)s::INTEGER[], -- "location[2]"
			%(Biomes.ids)s::INTEGER[], -- "Biomes.id"
			%(notes)s::TEXT[] -- "notes"
		) AS "Temp" ("title", "dimension", "location_x", "location_y", "location_z", "Biomes.id", "notes")
		RETURNING "id";
	"""

	titles: list[str] = [location.title for location in locations]
	dimensions: list[str] = [location.dimension for location in locations]
	locations_x: list[list[int]] = [location.location[0] for location in locations]
	locations_y: list[list[int]] = [location.location[1] for location in locations]
	locations_z: list[list[int]] = [location.location[2] for location in locations]
	biomes: list[str] = [location.biome.id if(location.biome is not None) else None for location in locations]
	notes: list[str] = [location.notes for location in locations]

	await cursor.execute(
		query,
		{
			"Worlds.id": locations[0].world.id,
			"titles": titles,
			"dimensions": dimensions,
			"locations_x": locations_x,
			"locations_y": locations_y,
			"locations_z": locations_z,
			"Biomes.ids": biomes,
			"notes": notes,
		}
	)

	location_ids: list[int] = [row["id"] async for row in cursor]
	for location_id, location in zip(location_ids, locations):
		location.id = location_id


@connect
async def set_title(cursor: psycopg.AsyncCursor, location_id: int, title: str) -> dict:
	query = """UPDATE "Locations" SET "title" = %(title)s WHERE "id" = %(id)s;"""
	await cursor.execute(query, {"title": title, "id": location_id})


@connect
async def unfavorite_location(cursor: psycopg.AsyncCursor, location_id: int) -> dict:
	query = """UPDATE "Locations" SET "favorited" = NULL WHERE "id" = %(id)s;"""
	await cursor.execute(query, {"id": location_id})
