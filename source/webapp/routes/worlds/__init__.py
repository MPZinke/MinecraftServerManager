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


import asyncio
from io import BytesIO
from pathlib import Path
import shutil
from threading import Thread
import traceback


from quart import jsonify, redirect, render_template, request, send_file, Blueprint


from database.classes import Version, World
from database.queries.versions import get_versions
from database.queries.worlds import (
	delete_world,
	get_world,
	get_worlds,
	new_world,
	set_world_exiting,
	set_world_running,
	set_world_starting,
	set_world_state,
	set_world_stopped,
)
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
	print(await request.files)
	file = next((await request.files).values(), None)
	world = World(
		id=0,
		container_id=None,
		created=None,
		data=file.read() if(file is not None) else None,
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


@worlds_blueprint.get("/worlds/<int:world_id>")
async def GET_worlds_world(world_id: int):
	world: World = get_world(world_id)
	return await render_template("worlds/world/index.j2", world=world)


@worlds_blueprint.get("/worlds/<int:world_id>/delete")
async def GET_worlds_world_delete(world_id: int):
	world = get_world(world_id)
	if(world.state == "offline"):
		delete_world(world_id)
	return redirect("/worlds")


@worlds_blueprint.get("/worlds/<int:world_id>/start")
async def GET_worlds_world_start(world_id: int):
	world: World = get_world(world_id)

	if(world.state == "offline"):
		set_world_starting(world)  # Set it before page reload for snappier UI.

		async def start_world():
			try:
				data_path = Path(f"/Users/mpzinke/Workspace/world-{world.id}")
				await world.write_data(data_path)
				container = Container(world)
				await container.run(data_path)

				set_world_running(world)

			except Exception:
				traceback.print_exc()
				set_world_stopped(world)
				raise

		asyncio.create_task(start_world())

	return redirect(f"/worlds/{world_id}")


@worlds_blueprint.get("/worlds/<int:world_id>/state")
async def GET_worlds_world_state(world_id: int):
	world = get_world(world_id)

	return jsonify(
		{
			"run_button": await render_template("worlds/world/run_button.j2", world=world),
			"port": world.port if(world.port is not None) else "-",
			"state": world.state,
		}
	)



@worlds_blueprint.get("/worlds/<int:world_id>/stop")
async def GET_worlds_world_stop(world_id: int):
	world = get_world(world_id)

	if(world.state == "running"):
		set_world_exiting(world)

		async def stop_world():
			container = Container(world)
			try:
				await container.stop()
			except Exception:
				world.state = "running"
				set_world_state(world)
				traceback.print_exc()
				return

			data_path = Path(f"/Users/mpzinke/Workspace/world-{world.id}")
			await world.read_data(data_path)
			set_world_stopped(world)
			shutil.rmtree(data_path)

		asyncio.create_task(stop_world())

	return redirect(f"/worlds/{world_id}")


@worlds_blueprint.get("/worlds/<int:world_id>/download")
async def GET_worlds_world_download(world_id: int):
	world = get_world(world_id)

	file = BytesIO(world.data)
	return await send_file(file, attachment_filename=f"""{world.name}_data.tar.gz""")
