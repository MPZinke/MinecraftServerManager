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


from quart import jsonify, redirect, render_template, request, send_file, Blueprint


from database.classes import Version, World
from database.queries.versions import get_versions
from database.queries.worlds import (
	delete_world,
	get_world,
	get_worlds,
	new_world,
	set_world_building,
	set_world_container,
	set_world_exiting,
	set_world_image,
	set_world_stop,
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
		set_world_building(world)  # Set it before page reload for snappier UI.

		def start():
			try:
				image = Image.build(world)
				world.image_id = image.id
				set_world_image(world)

				container = Container.run(image)
				world.container_id = container.id
				world.port = container.port
				set_world_container(world)

			except Exception as error:
				set_world_stop(world)
				raise

		Thread(target=start).start()

	return redirect(f"/worlds/{world_id}")


@worlds_blueprint.get("/worlds/<int:world_id>/state")
async def GET_worlds_world_state(world_id: int):
	world = get_world(world_id)

	return jsonify(
		{
			"run_button": await render_template("worlds/world/run_button.j2", world=world),
			"container_id": world.container_id if(world.container_id is not None) else "-",
			"image_id": world.image_id if(world.image_id is not None) else "-",
			"port": world.port if(world.port is not None) else "-",
			"state": world.state,
		}
	)



@worlds_blueprint.get("/worlds/<int:world_id>/stop")
async def GET_worlds_world_stop(world_id: int):
	world = get_world(world_id)

	if(world.state == "running"):
		set_world_exiting(world)

		def stop():
			container = Container(world.container_id, Image(world.image_id), world.port)
			world.data = container.stop()
			set_world_stop(world)
			container.image.remove()

		Thread(target=stop).start()

	return redirect(f"/worlds/{world_id}")


@worlds_blueprint.get("/worlds/<int:world_id>/download")
async def GET_worlds_world_download(world_id: int):
	world = get_world(world_id)

	file = BytesIO(world.data)
	return await send_file(file, attachment_filename=f"""{world.name}_data.tar.gz""")
