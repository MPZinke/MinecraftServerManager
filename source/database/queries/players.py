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
async def get_player(cursor: psycopg.AsyncCursor, player_id: int) -> list[Player]:
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
