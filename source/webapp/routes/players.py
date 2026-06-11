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


from quart import render_template, Blueprint


from database.classes import Player
from database.queries.players import get_players


players_blueprint = Blueprint('players_blueprint', __name__)


@players_blueprint.get("/players")
async def GET_players():
	players: list[Player] = await get_players()
	return await render_template("players/index.j2", players=players)
