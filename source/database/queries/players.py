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
from database.classes import Player


@connect
def get_player(cursor: psycopg2.extras.RealDictCursor, player_id: int) -> list[Player]:
	query = """
		SELECT *
		FROM "Players"
		WHERE "id" = %s;
	"""
	cursor.execute(query, (player_id,))

	player_dict: dict = cursor.fetchone()
	return Player.from_dict(**player_dict)


@connect
def get_players(cursor: psycopg2.extras.RealDictCursor) -> list[Player]:
	query = """
		SELECT *
		FROM "Players";
	"""
	cursor.execute(query)

	return list(map(lambda player_dict: Player.from_dict(**player_dict), cursor))
