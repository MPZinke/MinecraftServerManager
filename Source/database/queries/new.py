

from datetime import datetime
import psycopg2.extras
from typing import Optional


from database.connect import connect


# @connect
# def new_version(cursor: psycopg2.extras.RealDictCursor, jar: bytes, released: datetime, tag: str) -> dict:
# 	query = """
# 		INSERT INTO "Versions" ("jar", "released", "tag") VALUES
# 		(%s, %s, %s)
# 		RETURNING *;
# 	"""

# 	cursor.execute(query, (jar, released, tag))
# 	return dict(cursor.fetchone())


@connect
def new_world(cursor: psycopg2.extras.RealDictCursor, name: int, data: Optional[bytes]=None, notes: str="",
	version_id: Optional[int]=None
) -> dict:
	query = """
		INSERT INTO "Worlds" ("name", "data", "notes", "Versions.id") VALUES
		(%s, %s, %s, %s)
		RETURNING *;
	"""

	cursor.execute(query, (name, data, notes, version_id))
	return dict(cursor.fetchone())
