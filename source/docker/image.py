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
import tarfile


import aiohttp


from database.classes import Version
from docker.api import request_json


class Image:
	DOCKERFILE = (
		b"""FROM openjdk:27-ea-slim\n"""
		b"""COPY ./server.jar /usr/games/server.jar\n"""
		b"""WORKDIR /usr/app/\n"""
		b"""EXPOSE 25565\n"""
		b"""ENTRYPOINT ["java", "-Xmx1024M", "-Xms1024M", "-jar", "/usr/games/server.jar", "nogui"]\n"""
		b"""CMD []\n"""
	)
	TAG_FORMAT = "minecraft:{version.tag}"


	def __init__(self, version: Version):
		self.tag: str = self.TAG_FORMAT.format(version=version)
		self.version: Version = version


	async def build(self) -> None:
		"""
		Build a docker image for this object's version.
		"""
		# Get server.jar.
		jar_file = BytesIO()
		async with aiohttp.ClientSession() as session:
			async with session.get(self.version.url) as response:
				response.raise_for_status()
				while(chunk := await response.content.read(1024)):
					jar_file.write(chunk)

		jar_file.seek(0)
		raw_jar_file = jar_file.read()

		# Create archive data.
		data = BytesIO()
		with tarfile.open(fileobj=data, mode="w") as archive:
			tar_info = tarfile.TarInfo(name="Dockerfile")
			tar_info.size = len(self.DOCKERFILE)
			archive.addfile(tar_info, BytesIO(self.DOCKERFILE))

			tar_info = tarfile.TarInfo(name="server.jar")
			tar_info.size = len(raw_jar_file)
			archive.addfile(tar_info, BytesIO(raw_jar_file))

		data.seek(0)

		# Build docker image.
		# From: https://docs.docker.com/reference/api/engine/version/v1.47/#tag/Image/operation/ImageBuild
		try:
			await request_json(
				"build",
				"POST",
				params={"t": self.tag, "q": "true"},
				headers={"Content-Type": "application/x-tar"},
				data=data.read()
			)

		except Exception as cause:
			raise Exception(f"Failed to build docker image.") from cause


	async def exists(self) -> bool:
		try:
			return await request_json(f"images/{self.tag}/json", quiet=True) is not None

		except Exception as cause:
			raise Exception(f"Failed to check docker images.") from cause
