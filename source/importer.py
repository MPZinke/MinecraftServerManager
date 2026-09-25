

import json


from jsonschema import validate
from quart.datastructures import FileStorage


from database.classes import Version, World
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
					"enum": ["overworld", "nether", "end"],
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

	print(len(bytes.fromhex(world_dict["data"])))

	world = World(
		id=0,
		created=None,
		container_id=None,
		data=bytes.fromhex(world_dict["data"]),
		last_played=None,
		name=name,
		notes=notes,
		port=None,
		seed=None,
		state="offline",
		version=Version(
			id=world_dict["version"],
			released=None,
			tag=None,
			title=None,
			url=None,
		),
	)
	# TODO: Insert world, locations
