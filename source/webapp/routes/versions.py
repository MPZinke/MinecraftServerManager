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


from datetime import datetime


from quart import redirect, render_template, request, Blueprint


from database.classes import Version
from database.queries.versions import get_versions, new_version


versions_blueprint = Blueprint('versions_blueprint', __name__)


@versions_blueprint.get("/versions")
async def GET_versions():
	versions = get_versions()
	return await render_template("versions/index.j2", versions=versions)


@versions_blueprint.get("/versions/new")
async def GET_versions_new():
	versions: list[Version] = get_versions()
	return await render_template("versions/new.j2", versions=versions)


@versions_blueprint.post("/versions/new")
async def POST_versions_new():
	version = Version(
		id=0,
		released=datetime.strptime("%Y-%m-%d", request.form["released-input"]),
		tag=request.form["tag-input"],
		title=request.form["title-input"],
		url=request.form["url-input"],
	)
	new_version(version)

	return redirect("/versions")
