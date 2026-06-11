#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.29                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


import asyncio
from typing import Awaitable


from quart import redirect, render_template, request, Blueprint


from database.classes import Player, World
from database.queries.players import get_player, get_players
from database.queries.worlds import get_world
from docker.minecraft import op_player


worlds_world_commands_blueprint = Blueprint('worlds_world_commands_blueprint', __name__)


@worlds_world_commands_blueprint.get("/worlds/<int:world_id>/commands")
async def GET_worlds_world_commands(world_id: int):
	world_promise: Awaitable[World] = get_world(world_id)
	players_promise: Awaitable[list[Player]] = get_players()
	world, players = await asyncio.gather(world_promise, players_promise)  # : World, list[Player]

	return await render_template("worlds/world/commands.j2", world=world, players=players)


@worlds_world_commands_blueprint.post("/worlds/<int:world_id>/commands/op")
async def POST_worlds_world_commands_op(world_id: int):
	form = await request.form
	player_id: int = int(form["player-select"])

	world_promise: Awaitable[World] = get_world(world_id)
	player_promise: Awaitable[Player] = get_player(player_id)
	world, player = await asyncio.gather(world_promise, player_promise)  # : World, Player

	if(world.state == "running"):
		await op_player(world.container_id, player.name)

	return redirect(f"/worlds/{world_id}/commands")
