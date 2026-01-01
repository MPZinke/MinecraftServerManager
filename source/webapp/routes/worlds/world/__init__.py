#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.27                                                                                                      #
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
	set_world_stopping,
	set_world_running,
	set_world_seed,
	set_world_starting,
	set_world_state,
	set_world_offline,
)
from docker import Container, Image
from logger import logger
from minecraft import get_seed, stop_server
from webapp.routes.worlds.world.commands import worlds_world_commands_blueprint
from webapp.routes.worlds.world.locations import worlds_world_locations_blueprint


worlds_world_blueprint = Blueprint('worlds_world_blueprint', __name__)
worlds_world_blueprint.register_blueprint(worlds_world_commands_blueprint)
worlds_world_blueprint.register_blueprint(worlds_world_locations_blueprint)


@worlds_world_blueprint.get("/worlds/<int:world_id>")
async def GET_worlds_world(world_id: int):
	world: World = get_world(world_id)
	return await render_template("worlds/world/index.j2", world=world)


@worlds_world_blueprint.post("/worlds/<int:world_id>/delete")
async def POST_worlds_world_delete(world_id: int):
	world = get_world(world_id)
	if(world.state == "offline"):
		delete_world(world_id)
	return redirect("/worlds")


@worlds_world_blueprint.post("/worlds/<int:world_id>/start")
async def POST_worlds_world_start(world_id: int):
	world: World = get_world(world_id)

	if(world.state == "offline"):
		set_world_starting(world)  # Set it before page reload for snappier UI.

		async def start_world():
			try:
				await world.write_data()
				container = Container(world)
				await container.run()

				set_world_running(world)

			except Exception:
				logger.error(traceback.format_exc())
				set_world_offline(world)
				raise

			if(world.seed is None):
				world.seed: int = await get_seed(world.container_id)
				set_world_seed(world)

		asyncio.create_task(start_world())

	return redirect(f"/worlds/{world_id}")


@worlds_world_blueprint.get("/worlds/<int:world_id>/state/json")
async def GET_worlds_world_state(world_id: int):
	world = get_world(world_id)

	return jsonify(
		{
			"container_id": world.container_id if(world.container_id is not None) else "-",
			"last_played": world.last_played.strftime("%Y-%m-%d %H:%M:%S") if(world.last_played is not None) else "-",
			"port": world.port if(world.port is not None) else "-",
			"run_button": await render_template("worlds/world/run_button.j2", world=world),
			"state": world.state,
		}
	)


@worlds_world_blueprint.post("/worlds/<int:world_id>/stop")
async def POST_worlds_world_stop(world_id: int):
	world = get_world(world_id)

	if(world.state == "running"):
		set_world_stopping(world)

		async def stop_world():
			try:
				if(not await stop_server(world.container_id)):  # Graceful shutdown.
					await Container(world).stop()  # Risky shutdown

			except Exception:
				world.state = "running"
				set_world_state(world)
				logger.error(traceback.format_exc())
				return

			await world.read_data()
			set_world_offline(world)
			shutil.rmtree(world._data_path)

		asyncio.create_task(stop_world())

	return redirect(f"/worlds/{world_id}")


@worlds_world_blueprint.get("/worlds/<int:world_id>/download")
async def GET_worlds_world_download(world_id: int):
	world = get_world(world_id)

	file = BytesIO(world.data)
	return await send_file(file, attachment_filename=f"""{world.name}_data.tar.gz""")
