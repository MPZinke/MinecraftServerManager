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
async def get_player(cursor: psycopg.AsyncCursor, player_id: int) -> Player:
	query = """
		SELECT *
		FROM "Players"
		WHERE "id" = %s;
	"""
	await cursor.execute(query, (player_id,))

	player_dict: dict = await cursor.fetchone()
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
async def add_unknown_players(cursor: psycopg.AsyncCursor, players: list[Player]) -> None:
	query = """
		INSERT INTO "Players" ("name", "uuid")
		SELECT "Player"."name", "Player"."uuid"::UUID
		FROM UNNEST(
			%s::TEXT[],
			%s::UUID[]
		) AS "Player" ("name", "uuid")
		WHERE "Player"."uuid" NOT IN (
			SELECT "uuid"
			FROM "Players"
		)
		RETURNING "id", "uuid";
	"""
	names: list[str] = [player.name for player in players]
	uuids: list[str] = [player.uuid for player in players]
	await cursor.execute(query, (names, uuids))

	async for row in cursor:
		player_id: int = row["id"]
		player_uuid: str = row["uuid"]
		for player in players:
			if(player.uuid == player_uuid):
				player.id = player_id
