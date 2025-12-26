#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.25                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


from io import BytesIO


from quart import redirect, render_template, request, send_file, Blueprint


from database.queries import get_versions, get_world, get_worlds_display_data, new_world
from server_processes import start_server, stop_server


worlds_blueprint = Blueprint('worlds_blueprint', __name__)


@worlds_blueprint.get("/")
@worlds_blueprint.get("/worlds")
async def GET_worlds():
	worlds = get_worlds_display_data()
	return await render_template("worlds/index.j2", worlds=worlds)


@worlds_blueprint.get("/worlds/new")
async def GET_worlds_new():
	versions = get_versions()
	return await render_template("worlds/new.j2", versions=versions)


@worlds_blueprint.post("/worlds/new")
async def POST_worlds_new():
	name = request.form["name"]
	notes = request.form["notes"]
	version_id = int(request.form["version_id"])
	new_world(name, None, notes, version_id)

	return redirect("/worlds")


@worlds_blueprint.get("/worlds/start/<int:world_id>")
async def POST_worlds_start(world_id: int):
	start_server(world_id)

	return redirect("/worlds")


@worlds_blueprint.get("/worlds/stop/<int:world_id>")
async def POST_worlds_stop(world_id: int):
	stop_server(world_id)

	return redirect("/worlds")


@worlds_blueprint.get("/worlds/download/<int:world_id>")
async def GET_worlds_download(world_id: int):
	world = get_world(world_id)

	file = BytesIO(world["data"])
	return await send_file(file, attachment_filename=f"""{world["name"]}_data.tar.gz""")
