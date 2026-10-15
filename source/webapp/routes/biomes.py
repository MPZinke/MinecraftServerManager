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


from quart import redirect, session, Blueprint


from database.classes import Biome
from database.exceptions import NoResults
from database.queries.biomes import get_biome, get_biomes
from webapp.wrappers import render_template


biomes_blueprint = Blueprint('biomes_blueprint', __name__)


@biomes_blueprint.get("/biomes")
async def GET_biomes():
	biomes: list[Biome] = await get_biomes()
	return await render_template("biomes/index.j2", biomes=biomes)


@biomes_blueprint.get("/biomes/<int:biome_id>")
async def GET_biomes_biome(biome_id: int):
	try:
		biome: Biome = await get_biome(biome_id)
		return await render_template("biomes/biome.j2", biome=biome)

	except NoResults:
		session["alert"] = f"No biome with id {biome_id} found"
		return redirect("/biomes")


@biomes_blueprint.get("/biomes/new")
async def GET_biomes_new():
	return await render_template("biomes/new.j2")


@biomes_blueprint.post("/biomes/new")
async def POST_biomes_new():
	...
	# TODO
