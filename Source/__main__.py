


# from datetime import datetime
from io import BytesIO
import os
from pathlib import Path
import tarfile


from flask import redirect, render_template, request, send_file, Flask


from database.queries import get_versions, get_world, get_worlds_display_data, new_world
from server_processes import start_server, stop_server


ROOT_DIR = str(Path(__file__).absolute().parent)
TEMPLATE_FOLDER = os.path.join(ROOT_DIR, "HTML/Templates")
STATIC_FOLDER = os.path.join(ROOT_DIR, "HTML/Static")


app = Flask("Catan", template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)


def compress_file(file: bytes) -> bytes:
	bytes_io_tar_file = BytesIO(file)
	with tarfile.open(fileobj=bytes_io_tar_file, mode="w:gz") as tar_file:
		tar_file.write(file)

	return bytes_io_tar_file.read()


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/versions")
def versions_GET():
	versions = get_versions()
	return render_template("Versions.j2", versions=versions)


# @app.route("/versions/new")
# def versions_new_GET():
# 	return render_template("NewVersion.j2")


# @app.route("/versions/new", methods=["POST"])
# def versions_new_POST():
# 	tag = request.form["tag"]
# 	released = datetime.strptime(request.form["released"], "%Y-%m-%d")
# 	file_data = request.files['file'].read()

# 	new_version(file_data, released, tag)

# 	return redirect("/versions")


@app.route("/worlds")
def worlds_GET():
	worlds = get_worlds_display_data()
	return render_template("Worlds.j2", worlds=worlds)


@app.route("/worlds/new")
def worlds_new_GET():
	versions = get_versions()
	return render_template("NewWorld.j2", versions=versions)


@app.route("/worlds/new", methods=["POST"])
def worlds_new_POST():
	name = request.form["name"]
	notes = request.form["notes"]
	version_id = int(request.form["version_id"])
	new_world(name, None, notes, version_id)

	return redirect("/worlds")


@app.route("/worlds/start/<int:world_id>", methods=["GET"])
def worlds_start_POST(world_id: int):
	start_server(world_id)

	return redirect("/worlds")


@app.route("/worlds/stop/<int:world_id>")
def worlds_stop_POST(world_id: int):
	stop_server(world_id)

	return redirect("/worlds")


@app.route("/worlds/download/<int:world_id>")
def worlds_download_GET(world_id: int):
	world = get_world(world_id)

	file = BytesIO(world["data"])
	return send_file(file, f"""{world["name"]}_data.tar.gz""")


app.run(host="0.0.0.0", port=80, debug=True)
