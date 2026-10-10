#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.28                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


from quart import datastructures, redirect, render_template, request, Blueprint


from database.classes import Version, World
from database.queries.versions import get_versions
from importer import (import_world_json, import_world_data_tar_gz)


worlds_new_blueprint = Blueprint('worlds_new_blueprint', __name__)


@worlds_new_blueprint.get("/worlds/new")
async def GET_worlds_new():
	version_id: int = int(request.args.get("version", "0"))
	versions: list[Version] = await get_versions()
	return await render_template("worlds/new.j2", versions=versions, version_id=version_id)


@worlds_new_blueprint.post("/worlds/new")
async def POST_worlds_new():
	form = await request.form
	file: datastructures.FileStorage = (await request.files)["file-input"]
	name: str = form["name-input"]
	notes: str = form["notes-input"]

	if(file.content_length == 0):
		data: bytes = bytes.fromhex("1f8b080070e5516902ffedd1310ec2301004c0ab79052f889cc840c56352b8a30ab694e763a541a227529499664fdb6c71a5bde6a1ae35fe2875f79cb7ec7e33a571fade5bffc8d32dae2976d0de755efa649c53e9ff7fd6a5954b00000000000000000070201ff03316c500280000")
		version_id: int = int(form["version_id-select"])
		world: World = await import_world_data_tar_gz(data, name, notes, version_id)

	elif(file.filename.endswith(".json")):
		world: World = await import_world_json(file, name, notes)

	elif(file.filename.endswith(".tar.gz")):
		version_id: int = int(form["version_id-select"])

		world: World = await import_world_data_tar_gz(file.read(), name, notes, version_id)

	else:
		...

	return redirect(f"/worlds/{world.id}")
