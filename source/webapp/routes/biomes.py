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


from database.classes import Biome
from database.queries.biomes import get_biomes


biomes_blueprint = Blueprint('biomes_blueprint', __name__)


@biomes_blueprint.get("/biomes")
async def GET_biomes():
	biomes: list[Biome] = get_biomes()
	print(len(biomes))
	return await render_template("biomes/index.j2", biomes=biomes)
