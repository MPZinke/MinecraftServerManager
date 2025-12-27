#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.26                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


from io import BytesIO
import os
from pathlib import Path
import requests
import shutil
import subprocess
import tarfile


from database.queries.worlds import set_world_image, set_world_state


class Image:
	DOCKERFILE = (
		"""FROM openjdk:27-ea-slim\n"""
		"""WORKDIR /usr/app/\n"""
		"""COPY ./* ./\n"""
		"""RUN rm Dockerfile\n"""
		"""EXPOSE 25565\n"""
		"""ENTRYPOINT ["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", "nogui"{bonus_chest}]\n"""
	)


	def __init__(self, id: str):
		self.id: str = id


	@staticmethod
	def build(world: object) -> object:
		# Create dockerfile.
		build_folder = Path(f"/tmp/minecraft_build-{world.id}")
		if(build_folder.exists()):
			shutil.rmtree(build_folder)

		build_folder.mkdir()

		with open(build_folder / "Dockerfile", "w") as file:
			file.write(Image.DOCKERFILE.format(bonus_chest=""", "--bonusChest" """ if(world.last_played is None) else ""))

		# Add server.jar.
		response: requests.Response = requests.get(world.version.url, stream=True, timeout=21)
		with open(os.path.join(build_folder, "server.jar"), "wb") as file:
			for chunk in response.iter_content(chunk_size=1024):
				file.write(chunk)

		# Add world.
		world_data_file = BytesIO(world.data)
		with tarfile.open(fileobj=world_data_file, mode="r:gz") as tar_file:
			tar_file.extractall(build_folder)

		# Docker build.
		build_process = subprocess.run(
			[
				"docker",
				"build",
				"--progress",
				"quiet",
				build_folder,
			],
			capture_output=True,
			check=True,
			text=True,
		)
		world.build_id = build_process.stdout.strip().replace("sha256:", "")

		return Image(world.build_id)


	def remove(self):
		subprocess.run(
			[
				"docker",
				"rmi",
				self.id
			],
			capture_output=True,
			check=True,
			text=True,
		)


	async def run(self) -> object:
		from docker import Container
		return await Container.run(self)
