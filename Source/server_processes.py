

from io import BytesIO
import os
import requests
import shutil
import socket
import subprocess
import tarfile


import docker


from database.queries import get_version, get_world, update_running_world, update_stopped_world


def run_output(command: list[str]) -> bytes:
	process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return process.stdout


def setup_build_folder(world: dict, version: dict) -> str:
	build_folder = f"""/tmp/minecraft_build-{world["id"]}"""

	if(os.path.exists(build_folder)):
		shutil.rmtree(build_folder)

	os.mkdir(build_folder)

	write_dockerfile(build_folder)
	download_server_jar(build_folder, version)
	write_world_data(build_folder, world["data"])

	return build_folder


def write_dockerfile(build_folder: str) -> None:
	with open(os.path.join(build_folder, "Dockerfile"), "w") as file:
		file.write(
			"""FROM openjdk:24-slim\n"""
			"""WORKDIR /usr/app/\n"""
			"""COPY ./* ./\n"""
			"""RUN rm Dockerfile\n"""
			"""EXPOSE 25565\n"""
			"""CMD ["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", "nogui", "--bonusChest"]\n"""
		)


def download_server_jar(build_folder: str, version: dict) -> None:
	response: requests.Response = requests.get(version["url"], stream=True, timeout=21)
	with open(os.path.join(build_folder, "server.jar"), "wb") as file:
		for chunk in response.iter_content(chunk_size=1024):
			file.write(chunk)


def write_world_data(build_folder: str, world_data: bytes) -> None:
	world_data_file = BytesIO(world_data)
	with tarfile.open(fileobj=world_data_file, mode="r:gz") as tar_file:
		tar_file.extractall(build_folder)


def compress_world_data(tar_data: bytes) -> bytes:
	compressed_bytes_file = BytesIO()
	with tarfile.open(fileobj=compressed_bytes_file, mode="w:gz") as compressed_file:
		with tarfile.open(fileobj=BytesIO(tar_data), mode="r") as tar_file:
			for file in tar_file.getmembers():
				if(file.name not in ["app", "app/server.jar", "app/server.1.21.jar"]):
					compressed_file.addfile(file, tar_file.extractfile(file))

	compressed_bytes_file.seek(0)
	return compressed_bytes_file.read()


def decompress_file(compressed_file: bytes) -> bytes:
	bytes_io_file = BytesIO(compressed_file)
	with tarfile.open(fileobj=bytes_io_file, mode="r:gz") as tar_file:
		return tar_file.read()


def get_available_port() -> int:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		if(s.connect_ex(('', 25565)) != 0):
			return 25565

	# FROM: https://stackoverflow.com/a/1365284
	sock = socket.socket()
	sock.bind(("localhost", 0))
	return sock.getsockname()[1]


def start_server(world_id: int) -> None:
	client = docker.from_env()

	world = get_world(world_id)
	version = get_version(world["Versions.id"])

	if(world["is_running"]):
		#TODO: Check if the world is actually running
		pass

	build_folder: str = setup_build_folder(world, version)
	subprocess.call(["docker", "build", "-t", world["image_tag"], build_folder])
	# shutil.rmtree(build_folder)

	port = get_available_port()
	update_running_world(world_id, port)

	subprocess.call(["docker", "run", "--detach", "--publish", f"25565:{port}", "--name", world["container_name"], world["image_tag"]])


def stop_server(world_id: int):
	world = get_world(world_id)

	if(not world["is_running"]):
		#TODO: Check if the world is actually stopped
		pass

	container_id: str = run_output(["docker", "ps", "-aqf", f"""name=^{world["container_name"]}$"""]).decode().strip()
	status = run_output(["docker", "ps", "--filter", f"id={container_id}", "--format", "{{.State}}"]).decode().strip()

	if(status != "paused"):
		subprocess.call(["docker", "pause", world["container_name"]])

	data: bytes = run_output(["docker", "cp", f"{container_id}:/usr/app", "-"])
	compressed_data = compress_world_data(data)
	update_stopped_world(world_id, compressed_data)

	subprocess.call(["docker", "kill", world["container_name"]])
	subprocess.call(["docker", "rm", world["container_name"]])
	subprocess.call(["docker", "rmi", world["image_tag"]])
