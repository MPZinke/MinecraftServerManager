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
from typing import Awaitable, Optional


from quart import redirect, render_template, request, Blueprint


from database.classes import Biome, Location, Player, World
from database.queries.biomes import get_biomes
from database.queries.locations import delete_location, get_location, get_locations_for_world, new_location
from database.queries.players import get_player, get_players
from database.queries.worlds import get_world
from docker.minecraft import get_player_location, teleport_player


worlds_world_locations_blueprint = Blueprint('worlds_world_locations_blueprint', __name__)


@worlds_world_locations_blueprint.get("/worlds/<int:world_id>/locations")
async def GET_worlds_world_locations(world_id: int):
	world: World = await get_world(world_id)
	locations: list[Location] = await get_locations_for_world(world)
	return await render_template("worlds/world/locations/index.j2", world=world, locations=locations)


@worlds_world_locations_blueprint.get("/worlds/<int:world_id>/locations/new")
async def GET_worlds_world_locations_new(world_id: int):
	world_promise: Awaitable[World] = get_world(world_id)
	biomes_promise: Awaitable[list[Biome]] = get_biomes()
	players_promise: Awaitable[list[Player]] = get_players()
	# World, list[Biome], list[Player]
	world, biomes, players = await asyncio.gather(world_promise, biomes_promise, players_promise)
	return await render_template("worlds/world/locations/new.j2", biomes=biomes, players=players, world=world)


@worlds_world_locations_blueprint.post("/worlds/<int:world_id>/locations/new")
async def POST_worlds_world_locations_new(world_id: int):
	form: dict = await request.form
	player_id: int = int(form["player-select"])
	title: str = form["title-input"]
	biome: Optional[int] = int(form["biome-select"] or "0") or None
	notes: str = form["notes-textarea"]

	world_promise: Awaitable[World] = get_world(world_id)
	player_promise: Awaitable[Player] = get_player(player_id)
	world, player = await asyncio.gather(world_promise, player_promise)  # : World, Player
	if(world.state == "running"):
		# Optional[str], Optional[Tuple[int, int, int]]
		dimension, location = await get_player_location(world.container_id, player.name)

		# TODO: If None, None: redirect to error page.

		location = Location(
			id=0,
			title=title,
			dimension=dimension,
			location=location,
			notes=notes,
			world=world,
			biome=Biome(
				id=biome,
				dimension=None,
				title=None,
				description=None,
			),
		)
		await new_location(location)

	return redirect(f"/worlds/{world_id}/locations")


@worlds_world_locations_blueprint.post("/worlds/<int:world_id>/locations/<int:location_id>/delete")
async def POST_worlds_world_locations_location_delete(world_id: int, location_id: int):
	await delete_location(location_id)
	return redirect(f"/worlds/{world_id}/locations")


@worlds_world_locations_blueprint.post("/worlds/<int:world_id>/locations/<int:location_id>/tp")
async def POST_worlds_world_locations_location_tp(world_id: int, location_id: int):
	world_promise: Awaitable[World] = get_world(world_id)
	location_promise: Awaitable[Location] = get_location(location_id)
	world, location = await asyncio.gather(world_promise, location_promise)  # : World, Location

	await teleport_player(world.container_id, "MPZinke", location.location, location.dimension)

	return redirect(f"/worlds/{world_id}/locations")
