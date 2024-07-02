#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2024.07.02                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


from datetime import datetime
import psycopg2.extras
from typing import Optional


from database.connect import connect


@connect
def update_running_world(cursor: psycopg2.extras.RealDictCursor, world_id: int, mapped_port: int) -> dict:
	query = """
		UPDATE "Worlds"
		SET "is_running" = TRUE, "last_played" = %s, "mapped_port" = %s
		WHERE "id" = %s
		RETURNING *;
	"""

	cursor.execute(query, (datetime.now(), mapped_port, world_id))
	return dict(cursor.fetchone())


@connect
def update_stopped_world(cursor: psycopg2.extras.RealDictCursor, world_id: int, data: bytes) -> dict:
	query = """
		UPDATE "Worlds"
		SET "is_running" = FALSE, "mapped_port" = NULL, "last_played" = %s, "data" = %s
		WHERE "id" = %s
		RETURNING *;
	"""

	cursor.execute(query, (datetime.now(), data, world_id))
	return dict(cursor.fetchone())
