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
from database.classes import Biome


@connect
async def get_biomes(cursor: psycopg.AsyncCursor) -> list[Biome]:
	query = """
		SELECT *
		FROM "Biomes"
		ORDER BY "title";
	"""

	await cursor.execute(query)
	biome_dicts: list[dict] = [biome_dict async for biome_dict in cursor]
	return list(map(lambda biome_dict: Biome.from_dict(**biome_dict), biome_dicts))
