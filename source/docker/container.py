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
import socket


from database.classes import World
from docker.image import Image
from logger import logger


class Container:
	SERVICE_LABEL = "managed-minecraft-server"
	RUNNING = "running"


	def __init__(self, world: World):
		self.world: World = world


	async def run(self):
		image = Image(self.world.version)
		if(not await image.exists()):
			logger.info("Image does not exist. Building it now.")
			await image.build()

		# Get an available port.
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			if(s.connect_ex(('', 25565)) != 0):
				self.world.port: int = 25565

		if(self.world.port is None):
			# FROM: https://stackoverflow.com/a/1365284
			sock = socket.socket()
			sock.bind(("localhost", 0))
			self.world.port: int = sock.getsockname()[1]

		logger.info(f"Allocated port {self.world.port} for world '{self.world.name}'.")

		command_args: list[str] = []  # Default to preexisting command_args
		if(self.world.last_played is None):
			logger.info("Adding bonus chest.")
			command_args.append("--bonusChest")

		process = await asyncio.create_subprocess_exec(
			"docker",
			"run",
			"--detach",
			"--interactive",
			"--rm",
			"--tty",
			"--label",
			f"service={self.SERVICE_LABEL}",
			"--publish",
			f"{self.world.port}:25565",
			"--volume",
			f"{self.world._data_path}:/usr/app",
			image.reference,
			*command_args,
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		stdout, stderr = map(lambda io: io.decode().strip(), await process.communicate())
		if(process.returncode != 0):
			raise Exception(f"Failed to run docker container with stderr: {stderr}")

		self.world.container_id = stdout
		logger.info(f"Started container {self.world.container_id}.")


	async def state(self) -> str:
		process = await asyncio.create_subprocess_exec(
			"docker",
			"ps",
			"--all",
			"--filter",
			f"id={self.world.container_id}",
			"--format",
			"{{.State}}",
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		stdout, stderr = map(lambda io: io.decode().strip(), await process.communicate())
		if(process.returncode != 0):
			raise Exception(f"Failed to check docker container with stderr: {stderr}")

		return stdout


	async def stop(self) -> None:
		process = await asyncio.create_subprocess_exec(
			"docker",
			"stop",
			self.world.container_id,
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		_stdout, stderr = map(lambda io: io.decode().strip(), await process.communicate())
		if(process.returncode != 0):
			raise Exception(f"Failed to stop docker container with stderr: {stderr}")

		logger.info(f"Stopped container {self.world.container_id}")
