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


from quart import redirect, request, session, Blueprint


from database.classes import Player, World
from database.exceptions import NoResults
from database.queries.players import get_players
from database.queries.worlds import get_world
from docker.minecraft import op_player, time_set_0
from webapp.wrappers import render_template


worlds_world_commands_blueprint = Blueprint('worlds_world_commands_blueprint', __name__)


@worlds_world_commands_blueprint.get("/worlds/<int:world_id>/commands")
async def GET_worlds_world_commands(world_id: int):
	try:
		world_promise: Awaitable[World] = get_world(world_id)
		players_promise: Awaitable[list[Player]] = get_players()
		world, players = await asyncio.gather(world_promise, players_promise)  # : World, list[Player]

	except NoResults:
		session["alert"] = f"No world with id {world_id} found."
		return redirect("/worlds")

	return await render_template("worlds/world/commands.j2", world=world, players=players)


@worlds_world_commands_blueprint.post("/worlds/<int:world_id>/commands/op")
async def POST_worlds_world_commands_op(world_id: int):
	form = await request.form
	player: str = form["player-select"]

	try:
		world: World = await get_world(world_id)

	except NoResults:
		session["alert"] = f"No world with id {world_id} found."
		return redirect("/worlds")

	if(world.state == "running"):
		await op_player(world.container_id, player)

	return redirect(f"/worlds/{world_id}/commands")


@worlds_world_commands_blueprint.post("/worlds/<int:world_id>/commands/time_set_0")
async def POST_worlds_world_commands_time_set_0(world_id: int):
	try:
		world: World = await get_world(world_id)

	except NoResults:
		session["alert"] = f"No world with id {world_id} found."
		return redirect("/worlds")

	if(world.state == "running"):
		await time_set_0(world.container_id)

	return redirect(f"/worlds/{world_id}/commands")
