

from io import BytesIO
import os
import shutil
import socket
import tarfile
import gzip


import docker


from database.queries import get_version, get_world, update_running_world, update_stopped_world


def setup_build_folder(world: dict, version: dict) -> str:
	build_folder = "/tmp/minecraft_build"

	if(os.path.exists(build_folder)):
		shutil.rmtree(build_folder)

	os.mkdir(build_folder)

	write_dockerfile(build_folder)
	write_server_jar(build_folder, version)
	write_world_data(build_folder, world["data"])

	return build_folder


def write_dockerfile(build_folder: str) -> None:
	with open(os.path.join(build_folder, "Dockerfile"), "w") as file:
		file.write(
			"""FROM openjdk:24-slim\n"""
			"""WORKDIR /usr/app\n"""
			"""COPY ./* ./\n"""
			"""RUN rm Dockerfile\n"""
			"""EXPOSE 25565\n"""
			"""CMD ["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", "nogui", "--bonusChest"]\n"""
		)


def write_server_jar(build_folder: str, version: dict) -> None:
	with open(os.path.join(build_folder, "server.jar"), "wb") as file:
		file.write(version["jar"])


def write_world_data(build_folder: str, world_data: bytes) -> None:
	world_data_file = BytesIO(world_data)
	# with tarfile.open(fileobj=world_data_file, mode="r") as tar_file:
	with tarfile.open(fileobj=world_data_file, mode="r:gz") as tar_file:
		tar_file.extractall(build_folder)


def compress_world_data(tar_data: bytes) -> bytes:
	compressed_bytes_file = BytesIO()
	with tarfile.open(fileobj=compressed_bytes_file, mode="w:gz") as compressed_file:
		with tarfile.open(fileobj=BytesIO(tar_data), mode="r") as tar_file:
			for file in tar_file.getmembers():
				compressed_file.addfile(file, tar_file.extractfile(file))

	compressed_bytes_file.seek(0)
	return compressed_bytes_file.read()


def decompress_file(compressed_file: bytes) -> bytes:
	bytes_io_file = BytesIO(compressed_file)
	with tarfile.open(fileobj=bytes_io_file, mode="r:gz") as tar_file:
		return tar_file.read()


def get_available_port() -> int:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		if(s.connect_ex(('localhost', 25565)) == 0):
			return 25565

	# FROM: https://stackoverflow.com/a/1365284
	sock = socket.socket()
	sock.bind(("localhost", 0))
	return sock.getsockname()[1]


def start_server(world_id: int) -> None:
	client = docker.from_env()

	world = get_world(world_id)
	version = get_version(world["Versions.id"])

	build_folder: str = setup_build_folder(world, version)
	client.images.build(path=build_folder, tag=world["image_tag"])
	shutil.rmtree(build_folder)

	port = get_available_port()
	update_running_world(world_id, port)

	client.containers.run(image=world["image_tag"], name=world["container_name"], ports={"25565/tcp": port}, detach=True)


def stop_server(world_id: int):
	world = get_world(world_id)

	client = docker.from_env()
	container = client.containers.get(world["container_name"])
	container.pause()
	data, _ = container.get_archive("/usr/app")
	data = b"".join(data)
	data = compress_world_data(data)

	update_stopped_world(world_id, data)
	container.kill()
	container.remove()
	client.images.remove(world["image_tag"])
