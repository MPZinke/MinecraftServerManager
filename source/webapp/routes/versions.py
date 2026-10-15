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


import psycopg
from quart import redirect, request, session, Blueprint


from database.classes import Version
from database.queries.versions import get_version, get_versions, new_version
from database.exceptions import NoResults
from webapp.wrappers import render_template


versions_blueprint = Blueprint('versions_blueprint', __name__)


@versions_blueprint.get("/versions")
async def GET_versions():
	versions = await get_versions()
	return await render_template("versions/index.j2", versions=versions)


@versions_blueprint.get("/versions/<int:version_id>")
async def GET_versions_version(version_id: int):
	try:
		version: Version = await get_version(version_id)
		return await render_template("versions/version.j2", version=version)

	except NoResults:
		session["alert"] = f"No version with id {version_id} found"
		return redirect("/versions")


@versions_blueprint.get("/versions/new")
async def GET_versions_new():
	versions: list[Version] = await get_versions()
	return await render_template("versions/new.j2", versions=versions)


@versions_blueprint.post("/versions/new")
async def POST_versions_new():
	try:
		version = Version(
			id=0,
			released=datetime.strptime("%Y-%m-%d", request.form["released-input"]),
			tag=request.form["tag-input"],
			title=request.form["title-input"],
			url=request.form["url-input"],
		)
		await new_version(version)

		return redirect("/versions")

	except psycopg.errors.UniqueViolation:
		session["alert"] = f"Version tag '{version.tag}' or title '{version.title}' already exists."
		return redirect("/players/new")
