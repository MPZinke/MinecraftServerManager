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
from threading import Thread


from quart import redirect, render_template, request, send_file, Blueprint


from database.classes import Version, World
from database.queries.versions import get_versions
from database.queries.worlds import get_world, get_worlds, new_world, set_world_container, set_world_stop
from docker import Container, Image


worlds_blueprint = Blueprint('worlds_blueprint', __name__)


@worlds_blueprint.get("/")
@worlds_blueprint.get("/worlds")
async def GET_worlds():
	worlds: list[World] = get_worlds()
	return await render_template("worlds/index.j2", worlds=worlds)


@worlds_blueprint.get("/worlds/new")
async def GET_worlds_new():
	versions: list[Version] = get_versions()
	return await render_template("worlds/new.j2", versions=versions)


@worlds_blueprint.post("/worlds/new")
async def POST_worlds_new():
	form = await request.form
	world = World(
		id=0,
		container_id=None,
		created=None,
		data=None,
		image_id=None,
		last_played=None,
		port=None,
		name=form["name-input"],
		notes=form["notes-input"],
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

	return redirect("/worlds")


@worlds_blueprint.get("/worlds/start/<int:world_id>")
async def GET_worlds_start_id(world_id: int):
	world: World = get_world(world_id)
	if(world.state in ["clean", "paused", "stopped"]):
		Thread(target=world.start).start()

	return redirect("/worlds")


@worlds_blueprint.get("/worlds/stop/<int:world_id>")
async def GET_worlds_stop_id(world_id: int):
	world = get_world(world_id)
	if(world.state == "running"):
		Thread(target=world.stop).start()

	return redirect("/worlds")


@worlds_blueprint.get("/worlds/download/<int:world_id>")
async def GET_worlds_download(world_id: int):
	world = get_world(world_id)

	file = BytesIO(world["data"])
	return await send_file(file, attachment_filename=f"""{world.name}_data.tar.gz""")
