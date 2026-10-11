#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.31                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


import asyncio
from typing import Awaitable


from quart import render_template, Blueprint


from database.classes import Player
from database.queries.players import get_player, get_players
from database.queries.worlds import get_running_worlds
from docker.minecraft import get_online_players, get_player_location


players_blueprint = Blueprint('players_blueprint', __name__)


@players_blueprint.get("/players")
async def GET_players():
	players: list[Player] = await get_players()
	return await render_template("players/index.j2", players=players)


@players_blueprint.get("/players/<int:player_id>")
async def GET_players_player(player_id: int):
	player: Player = await get_player(player_id)
	return await render_template("players/player/index.j2", player=player)


@players_blueprint.get("/players/<int:player_id>/world")
async def GET_players_player_world_json(player_id: int):
	player_promise: Awaitable[Player] = get_player(player_id)
	running_worlds_promise: Awaitable[Player] = get_running_worlds()

	player, running_worlds = await asyncio.gather(player_promise, running_worlds_promise)  # : Player, list[World]
	world_players_promises: list[Awaitable[list[Player]]] = []
	for running_world in running_worlds:
		world_players_promises.append(get_online_players(running_world.container_id))

	worlds_online_players: list[list[Player]] = await asyncio.gather(*world_players_promises)
	for running_world, online_players in zip(running_worlds, worlds_online_players):
		for online_player in online_players:
			if(online_player.uuid == player.uuid):
				dimension, location = await get_player_location(running_world.container_id, player.name)
				return await render_template(
					"players/player/world.j2",
					world=running_world,
					dimension=dimension,
					location=location
				)

	return ""
