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
from database.classes import Player


@connect
async def get_player(cursor: psycopg.AsyncCursor, id: int) -> Player:
	query = """
		SELECT *
		FROM "Players"
		WHERE "id" = %(id)s;
	"""
	await cursor.execute(query, {"id": id})

	player_dict: dict = await cursor.fetchone_or_fail()
	return Player.from_dict(**player_dict)


@connect
async def get_players(cursor: psycopg.AsyncCursor) -> list[Player]:
	query = """
		SELECT *
		FROM "Players";
	"""
	await cursor.execute(query)
	player_dicts: list[dict] = [player_dict async for player_dict in cursor]

	return list(map(lambda player_dict: Player.from_dict(**player_dict), player_dicts))


@connect
async def new_player(cursor: psycopg.AsyncCursor, player: Player) -> None:
	query = """
		INSERT INTO "Players" ("name", "uuid")
		VALUES
		(%(name)s, %(uuid)s)
		RETURNING "id";
	"""
	await cursor.execute(query, {"name": player.name, "uuid": player.uuid})
	player.id = (await cursor.fetchone_or_fail())["id"]


@connect
async def new_players(cursor: psycopg.AsyncCursor, players: list[Player]) -> None:
	query = """
		INSERT INTO "Players" ("name", "uuid")
		SELECT "Player"."name", "Player"."uuid"::UUID
		FROM UNNEST(
			%(names)s::TEXT[],
			%(uuids)s::UUID[]
		) AS "Player" ("name", "uuid")
		WHERE "Player"."uuid" NOT IN (
			SELECT "uuid"
			FROM "Players"
		)
		RETURNING "id", "uuid";
	"""
	names: list[str] = [player.name for player in players]
	uuids: list[str] = [player.uuid for player in players]
	await cursor.execute(query, {"names": names, "uuids": uuids})

	async for row in cursor:
		player_id: int = row["id"]
		player_uuid: str = row["uuid"]
		for player in players:
			if(player.uuid == player_uuid):
				player.id = player_id
