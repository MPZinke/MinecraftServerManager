

from typing import Any, Optional


import quart
from quart import session


async def render_template(*args: list, **kwargs: dict) -> Any:
	alert: Optional[str] = session.get("alert")
	if(alert is not None):
		del session["alert"]

	return await quart.render_template(*args, alert=alert, session=session, **kwargs)
