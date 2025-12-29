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


import asyncio
from pathlib import Path


import aiofiles
import aiohttp


from database.classes import Version


class Image:
	DOCKERFILE = (
		"""FROM openjdk:27-ea-slim\n"""
		"""COPY ./server.jar /usr/games/server.jar\n"""
		"""WORKDIR /usr/app/\n"""
		"""EXPOSE 25565\n"""
		"""ENTRYPOINT ["java", "-Xmx1024M", "-Xms1024M", "-jar", "/usr/games/server.jar", "nogui"]\n"""
		"""CMD []\n"""
	)
	REFERENCE_FORMAT = "minecraft:{version}"


	def __init__(self, version: Version):
		self.reference: str = self.REFERENCE_FORMAT.format(version=version.tag)
		self.version: Version = version


	async def build(self) -> None:
		# Create build directory.
		build_folder = Path(f"/tmp/minecraft_build-{self.version.tag}")
		if(not build_folder.exists()):
			build_folder.mkdir()

		# Create dockerfile in build directory.
		async with aiofiles.open(build_folder / "Dockerfile", 'w') as file:
			await file.write(self.DOCKERFILE)

		# Add server.jar.
		async with aiohttp.ClientSession() as session:
			async with session.get(self.version.url) as response:
				response.raise_for_status()
				async with aiofiles.open(build_folder / "server.jar", 'wb') as file:
					while(chunk := await response.content.read(1024)):
						await file.write(chunk)

		# Docker build.
		process = await asyncio.create_subprocess_exec(
			"docker",
			"build",
			"--tag",
			self.reference,
			"--progress",
			"quiet",
			build_folder,
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		_stdout, stderr = map(lambda io: io.decode().strip(), await process.communicate())
		if(process.returncode != 0):
			raise Exception(f"Failed to build docker image with stderr: {stderr}")


	async def exists(self) -> bool:
		process = await asyncio.create_subprocess_exec(
			"docker",
			"images",
			"--filter",
			f"reference={self.reference}",
			"--format",
			"{{.Repository}}:{{.Tag}}",
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		stdout, stderr = map(lambda io: io.decode().strip(), await process.communicate())
		if(process.returncode != 0):
			raise Exception(f"Failed to check docker images with stderr: {stderr}")

		return stdout != ""


	async def remove(self) -> None:
		process = await asyncio.create_subprocess_exec(
			"docker",
			"rmi",
			self.reference,
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		_stdout, stderr = map(lambda io: io.decode().strip(), await process.communicate())
		if(process.returncode != 0):
			raise Exception(f"Failed to remove docker image with stderr: {stderr}")
