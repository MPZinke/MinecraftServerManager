#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.28                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


from quart import redirect, render_template, request, Blueprint


from database.classes import Version, World
from database.queries.versions import get_versions
from database.queries.worlds import new_world


worlds_new_blueprint = Blueprint('worlds_new_blueprint', __name__)


@worlds_new_blueprint.get("/worlds/new")
async def GET_worlds_new():
	version_id: int = int(request.args.get("version", "0"))
	versions: list[Version] = get_versions()
	return await render_template("worlds/new.j2", versions=versions, version_id=version_id)


@worlds_new_blueprint.post("/worlds/new")
async def POST_worlds_new():
	form = await request.form
	data = (await request.files)["file-input"].read()
	world = World(
		id=0,
		created=None,
		data=data or None,
		last_played=None,
		name=form["name-input"],
		notes=form["notes-input"],
		port=None,
		state='clean',
		version=Version(
			id=int(form["version_id-select"]),
			released=None,
			tag=None,
			title=None,
			url=None,
		),
	)
	new_world(world)

	return redirect(f"/worlds/{world.id}")
