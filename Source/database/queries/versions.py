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


import psycopg2.extras


from database.connect import connect
from database.classes import Version


@connect
def get_version(cursor: psycopg2.extras.RealDictCursor, version_id: int) -> Version:
	query = """
		SELECT *
		FROM "Versions"
		WHERE "id" = %s
		ORDER BY "Versions"."id" ASC;
	"""

	cursor.execute(query, (version_id,))
	version_dict = cursor.fetchone()
	return Version.from_dict(**version_dict)


@connect
def get_versions(cursor: psycopg2.extras.RealDictCursor) -> list[Version]:
	query = """
		SELECT "id", "released", "tag", "title", "url"
		FROM "Versions"
		ORDER BY "Versions"."id" ASC;
	"""

	cursor.execute(query)
	return list(map(lambda version_dict: Version(**version_dict), cursor))
