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
from database.classes import Biome


@connect
def get_biomes(cursor: psycopg2.extras.RealDictCursor) -> list[Biome]:
	query = """
		SELECT *
		FROM "Biomes"
		ORDER BY "title";
	"""

	cursor.execute(query)
	return list(map(lambda biome_dict: Biome.from_dict(**biome_dict), cursor))
