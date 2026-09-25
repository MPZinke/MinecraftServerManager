

import asyncio
from datetime import datetime
import json
from typing import Optional


from jsonschema import validate
from quart.datastructures import FileStorage


from database.classes import Biome, Location, Version, World
from database.queries.biomes import get_biomes
from database.queries.locations import new_locations
from database.queries.worlds import new_world


schema = {
	"$schema": "https://json-schema.org/draft/2020-12/schema",
	"title": "World Json",
	"description": "A Minecraft world json",
	"type": "object",
	"required": [
		"created",
		"data",
		"last_played",
		"name",
		"notes",
		"seed",
		"version",
		"locations"
	],
	"properties": {
		"created": {
			"description": "The date a World was created.",
			"$ref": "#/$defs/datetime",
		},
		"locations": {
			"type": "array",
			"description": "The locations for a world.",
			"items": {
				"$ref": "#/$defs/location"
			}
		},
		"data": {
			"type": "string",
			"description": "The world data.",
			"pattern": "[0-9a-f]*"
		},
		"last_played": {
			"description": "The date a World was last played.",
			"$ref": "#/$defs/optional_datetime",
		},
		"name": {
			"description": "The name of a world.",
			"type": "string",
		},
		"notes": {
			"description": "The notes a world.",
			"type": "string",
		},
		"seed": {
			"type": ["integer", "null"],
			"description": "The world's seed.",
		},
		"version": {
			"type": "number",
			"description": "The world's version id.",
			"minimum": 1,
		},
	},

	"$defs": {
		"none": {
			"type": "null",
		},
		"datetime": {
			"type": "string",
			"pattern": r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
		},
		"optional_datetime": {
			"anyOf": [
				{"$ref": "#/$defs/datetime"},
				{"$ref": "#/$defs/none"},
			]
		},
		"location": {
			"type": "object",
			"required": [
				"title",
				"location",
				"dimension",
				"favorited",
				"biome",
				"notes",
			],
			"properties": {
				"title": {
					"type": "string",
					"description": "The location's title.",
				},
				"location": {
					"type": "array",
					"description": "The location's coordinates.",
					"items": {
						"type": "integer",
					},
					"minItems": 3,
					"maxItems": 3
				},
				"dimension": {
					"type": "string",
					"enum": ["overworld", "the_nether", "the_end"],
					"description": "The location's dimension.",
				},
				"favorited": {
					"$ref": "#/$defs/optional_datetime",
					"description": "When the locations was favorited.",
				},
				"biome": {
					"type": ["integer", "null"],
					"description": "The location's optional biome ID.",
				},
				"notes": {
					"type": "string",
				},
			},
		},
	},
}


def optional_string_to_optional_datetime(optional_string: Optional[str]) -> Optional[datetime]:
	if(optional_string is None):
		return None

	return datetime.strptime(optional_string, "%Y-%m-%d %H:%M:%S")


async def import_world_data_tar_gz(file: FileStorage, name: str, notes: str, version_id: int) -> World:
	data = file.read()
	world = World(
		id=0,
		created=None,
		container_id=None,
		data=data or None,
		last_played=None,
		name=name,
		notes=notes,
		port=None,
		seed=None,
		state="offline",
		version=Version(
			id=version_id,
			released=None,
			tag=None,
			title=None,
			url=None,
		),
	)
	await new_world(world)
	return world


async def import_world_json(file: FileStorage, name: str, notes: str) -> World:
	world_dict: dict = json.load(file)
	validate(world_dict, schema)

	world = World(
		id=0,
		created=optional_string_to_optional_datetime(world_dict["created"]),
		container_id=None,
		data=bytes.fromhex(world_dict["data"]),
		last_played=optional_string_to_optional_datetime(world_dict["last_played"]),
		name=name,
		notes=notes,
		port=None,
		seed=world_dict["seed"],
		state="offline",
		version=Version(
			id=world_dict["version"],
			released=None,
			tag=None,
			title=None,
			url=None,
		),
	)
	biomes_promise = get_biomes()
	new_world_promise = new_world(world)
	biomes, _ = await asyncio.gather(biomes_promise, new_world_promise)

	locations: list[Location] = []
	for location_dict in world_dict["locations"]:
		if(location_dict["biome"] is None):
			biome = None
		else:
			biome: Biome = next(filter(lambda biome: biome.id == location_dict["biome"], biomes))
			print(biome)

		location = Location(
			id=0,
			title=location_dict["title"],
			location=location_dict["location"],
			dimension=location_dict["dimension"],
			favorited=optional_string_to_optional_datetime(location_dict["favorited"]),
			world=world,
			biome=biome,
			notes=location_dict["notes"],
		)
		locations.append(location)

	await new_locations(locations)

	return world
	# TODO: Insert world, locations
