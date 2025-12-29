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


from typing import Optional, Tuple


from quart import redirect, render_template, request, Blueprint


from database.classes import Biome, Location, World
from database.queries.biomes import get_biomes
from database.queries.locations import get_locations_for_world, new_location
from database.queries.worlds import get_world
from docker import Container
from minecraft import get_player_location


worlds_world_locations_blueprint = Blueprint('worlds_world_locations_blueprint', __name__)


@worlds_world_locations_blueprint.get("/worlds/<int:world_id>/locations")
async def GET_worlds_world_locations(world_id: int):
	world: World = get_world(world_id)
	locations: list[Location] = get_locations_for_world(world)
	return await render_template("worlds/world/locations/index.j2", world=world, locations=locations)


@worlds_world_locations_blueprint.get("/worlds/<int:world_id>/locations/new")
async def GET_worlds_world_locations_new(world_id: int):
	world: World = get_world(world_id)
	biomes: list[Biome] = get_biomes()
	return await render_template("worlds/world/locations/new.j2", world=world, biomes=biomes)


@worlds_world_locations_blueprint.post("/worlds/<int:world_id>/locations/new")
async def POST_worlds_world_locations_new(world_id: int):
	form = await request.form
	title: str = form["title-input"]
	biome: Optional[int] = int(form["biome-select"] or "0") or None
	notes: str = form["notes-textarea"]
	world: World = get_world(world_id)

	location: Tuple[int, int, int] = get_player_location(Container(world), "MPZinke")  # TODO

	location = Location(
		id=0,
		title=title,
		location=location,
		notes=notes,
		world=world,
		biome=Biome(
			id=biome,
			title=None,
			world=None,
			description=None,
		),
	)

	new_location(location)

	return redirect(f"/worlds/{world_id}/locations")
	# return redirect(f"/worlds/{world_id}/locations/{location.id}")


@worlds_world_locations_blueprint.get("/worlds/<int:world_id>/locations/<int:location_id>")
async def GET_worlds_world_locations_location(world_id: int, location_id: int):
	world: World = get_world(world_id)
	return await render_template("worlds/world/locations/location/index.j2", world=world)
