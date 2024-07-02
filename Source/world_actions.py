

import os
import shutil


import docker


from database.queries.get import get_version, get_world


from io import BytesIO
import tarfile


def dockerfile() -> str:
	return (
		"""FROM openjdk:24-slim\n"""
		"""WORKDIR /usr/app\n"""
		"""COPY server.jar server.jar\n"""
		"""RUN echo 'eula=true' > eula.txt\n"""
		"""EXPOSE 25565\n"""
		"""CMD ["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", "nogui", "--bonusChest"]\n"""
	)


def decompress_file(compressed_file: bytes) -> bytes:
	bytes_io_file = BytesIO(compressed_file)
	with tarfile.open(fileobj=bytes_io_file, mode="r:gz") as tar_file:
		return tar_file.read()


def decompress_folder(compressed_folder: bytes, folder: str) -> None:
	bytes_io_file = BytesIO(compressed_folder)
	with tarfile.open(fileobj=bytes_io_file, mode="r:gz") as tar_file:
		tar_file.extractall(folder)


def start_world(world_id: int) -> None:
	world = get_world(world_id)
	version = get_version(world["Versions.id"])

	temp_folder = "/tmp/minecraft_build"
	if(os.path.exists(temp_folder)):
		shutil.rmtree(temp_folder)
	os.mkdir(temp_folder)

	# with open(temp_folder+"/Dockerfile", "wb") as file:
	# 	file.write(dockerfile_file)
	decompress_folder(world["data"], temp_folder)
	server_file = version["jar"]
	with open(temp_folder+"/server.jar", "wb") as file:
		file.write(server_file)

	dockerfile_file: str = dockerfile()
	with open(temp_folder+"/Dockerfile", "w") as file:
		file.write(dockerfile_file)

	client = docker.from_env()
	client.images.build(path=temp_folder, tag=world["image_tag"])


# def stop_world(world_id: int):
# 	pass
