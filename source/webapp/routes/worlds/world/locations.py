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
	set_world_exiting,
	set_world_running,
	set_world_starting,
	set_world_state,
	set_world_stopped,
)
from docker import Container, Image


worlds_world_locations_blueprint = Blueprint('worlds_world_locations_blueprint', __name__)


@worlds_world_locations_blueprint.get("/worlds/<int:world_id>/locations")
async def GET_worlds_world_locations(world_id: int):
	world: World = get_world(world_id)
	return await render_template("worlds/world/locations/index.j2", world=world)


@worlds_world_locations_blueprint.get("/worlds/<int:world_id>/locations/new")
async def GET_worlds_world_locations_new(world_id: int):
	world: World = get_world(world_id)
	return await render_template("worlds/world/locations/new.j2")


@worlds_world_locations_blueprint.post("/worlds/<int:world_id>/locations/new")
async def POST_worlds_world_locations_new(world_id: int):
	world: World = get_world(world_id)
	return await redirect(f"/worlds/{world_id}/locations/{location.id}")


@worlds_world_locations_blueprint.get("/worlds/<int:world_id>/locations/<int:location_id>")
async def GET_worlds_world_locations_location(world_id: int, location_id: int):
	world: World = get_world(world_id)
	return await render_template("worlds/world/locations/location/index.j2", world=world)
