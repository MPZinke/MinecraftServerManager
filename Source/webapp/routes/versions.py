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


from quart import redirect, render_template, request, Blueprint


from database.queries import get_versions


versions_blueprint = Blueprint('versions_blueprint', __name__)


@versions_blueprint.get("/versions")
async def GET_versions():
	versions = get_versions()
	return await render_template("versions/index.j2", versions=versions)


@versions_blueprint.get("/versions/new")
async def GET_versions_new():
	versions = get_versions()
	return await render_template("versions/new.j2", versions=versions)


@versions_blueprint.post("/versions/new")
async def POST_versions_new():
	released = request.form["released"]
	tag = request.form["tag"]
	title = request.form["title"]
	url = request.form["url"]
	new_version(released, tag, title, url)

	return redirect("/versions")
