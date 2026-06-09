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


import asyncio
from io import BytesIO
from pathlib import Path
import shutil
from threading import Thread
import traceback


from quart import jsonify, redirect, render_template, request, send_file, Blueprint


from database.classes import Version, World
from database.queries.versions import get_versions
from database.queries.worlds import get_worlds
from docker import Container, Image
from webapp.routes.biomes import biomes_blueprint
from webapp.routes.players import players_blueprint
from webapp.routes.versions import versions_blueprint
from webapp.routes.worlds import worlds_blueprint


root_blueprint = Blueprint('root_blueprint', __name__)
root_blueprint.register_blueprint(biomes_blueprint)
root_blueprint.register_blueprint(players_blueprint)
root_blueprint.register_blueprint(versions_blueprint)
root_blueprint.register_blueprint(worlds_blueprint)


@root_blueprint.get("/")
async def GET_():
	return await render_template("index.j2")
