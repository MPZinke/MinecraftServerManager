

import psycopg2.extras


from database.connect import connect


@connect
def get_version(cursor: psycopg2.extras.RealDictCursor, version_id: int) -> dict:
	query = """
		SELECT *
		FROM "Versions"
		WHERE "id" = %s;
	"""

	cursor.execute(query, (version_id,))
	return dict(cursor.fetchone())


@connect
def get_versions(cursor: psycopg2.extras.RealDictCursor) -> list[dict]:
	query = """
		SELECT *
		FROM "Versions";
	"""

	cursor.execute(query)
	return list(map(dict, cursor))


@connect
def get_world(cursor: psycopg2.extras.RealDictCursor, world_id: int) -> dict:
	query = """
		SELECT *
		FROM "Worlds"
		WHERE "id" = %s;
	"""

	cursor.execute(query, (world_id,))
	return dict(cursor.fetchone())


@connect
def get_worlds(cursor: psycopg2.extras.RealDictCursor) -> list[dict]:
	query = """
		SELECT "id", "created", "name", "notes", "last_played", "container_name", "image_tag", "is_running", "mapped_port"
		FROM "Worlds";
	"""

	cursor.execute(query)
	return list(map(dict, cursor))
