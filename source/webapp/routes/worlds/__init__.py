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
from webapp.routes.worlds.world import worlds_world_blueprint
from webapp.routes.worlds.new import worlds_new_blueprint


worlds_blueprint = Blueprint('worlds_blueprint', __name__)
worlds_blueprint.register_blueprint(worlds_world_blueprint)
worlds_blueprint.register_blueprint(worlds_new_blueprint)


@worlds_blueprint.get("/")
@worlds_blueprint.get("/worlds")
async def GET_worlds():
	worlds: list[World] = get_worlds()
	return await render_template("worlds/index.j2", worlds=worlds)
