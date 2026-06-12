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
import os
from pathlib import Path
import tarfile


from quart import Quart


from webapp.routes import root_blueprint
from updater import update_loop


WEBAPP_DIR = Path(__file__).parent
TEMPLATE_FOLDER = WEBAPP_DIR / "Templates"
STATIC_FOLDER = WEBAPP_DIR / "Static"


app = Quart("Minecraft Server Manager", template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
app.register_blueprint(root_blueprint)
app.config["MAX_CONTENT_LENGTH"] = 300 * (1024 ** 2)  # _ * MB



@app.before_serving
async def update():
	app.background_task = asyncio.ensure_future(update_loop())


@app.after_serving
async def shutdown():
    app.background_task.cancel()
    await asyncio.gather(app.background_task, return_exceptions=True)
