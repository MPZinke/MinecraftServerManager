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
from database.classes import Version


@connect
async def get_version(cursor: psycopg.AsyncCursor, version_id: int) -> Version:
	query = """
		SELECT *
		FROM "Versions"
		WHERE "id" = %s
		ORDER BY "Versions"."id" ASC;
	"""
	await cursor.execute(query, (version_id,))

	version_dict = await cursor.fetchone()
	return Version.from_dict(**version_dict)


@connect
async def get_versions(cursor: psycopg.AsyncCursor) -> list[Version]:
	query = """
		SELECT "id", "released", "tag", "title", "url"
		FROM "Versions"
		ORDER BY "Versions"."id" ASC;
	"""
	await cursor.execute(query)
	version_dicts: list[dict] = [version_dict async for version_dict in cursor]

	return list(map(lambda version_dict: Version(**version_dict), version_dicts))


@connect
async def new_version(cursor: psycopg.AsyncCursor, version: Version) -> None:
	query = """
		INSERT INTO "Worlds" ("released", "tag", "title", "url") VALUES
		(%s, %s, %s, %s)
		RETURNING "id";
	"""
	await cursor.execute(query, (version.released, version.tag, version.title, version.url))

	version.id = (await cursor.fetchone())["id"]
