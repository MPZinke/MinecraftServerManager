

import os
import psycopg
from psycopg.rows import dict_row


def connect(function: callable) -> callable:
	"""
	SUMMARY: Wraps a DB function with calls to connect and closes the DB.
	PARAMS:  Takes the function that will be wrapped.
	RETURNS: The function pointer that wraps the function.
	"""
	async def wrapper(*args: list, **kwargs: dict) -> list|dict:
		"""
		DETAILS: Creates a connection and passes it to the calling function.
		RETURNS: Value(s) if values.
		THROWS:  Whatever exceptions occur during function call.
		"""
		DB_user: str = os.getenv("MINECRAFT_DB_USER")
		DB_host: str = os.getenv("MINECRAFT_DB_HOST")
		DB_password: str = os.getenv("MINECRAFT_DB_PASSWORD")

		# FROM: https://www.psycopg.org/psycopg3/docs/api/connections.html#the-asyncconnection-class

		connection_string = f"host={DB_host} dbname=Minecraft user={DB_user} password={DB_password}"
		async with await psycopg.AsyncConnection.connect(
			connection_string,
			autocommit=True,
			row_factory=dict_row
		) as connection:
			async with connection.cursor() as cursor:
				results: list|dict = await function(cursor, *args, **kwargs)
				return results

	wrapper.__name__ = function.__name__
	return wrapper
