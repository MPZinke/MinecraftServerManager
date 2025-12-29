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
from io import BytesIO
from pathlib import Path
import shutil
import socket
import subprocess
import tarfile
from typing import Optional


from database.classes import World
from docker.image import Image


class Container:
	EXITED = "exited"
	PAUSED = "paused"
	RUNNING = "running"


	def __init__(self, world: World):
		self.name: str = f"minecraft-{world.id}"
		self.world: World = world


	async def run(self, data_path: Path):
		image = Image(self.world.version)
		if(not await image.exists()):
			print("Image does not exist. Building it now.")
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

		command_args: list[str] = []  # Default to preexisting command_args
		if(self.world.last_played is None):
			command_args.append("--bonusChest")

		process = await asyncio.create_subprocess_exec(
			"docker",
			"run",
			"--detach",
			"--interactive",
			"--rm",
			"--tty",
			"--name",
			self.name,
			"--publish",
			f"{self.world.port}:25565",
			"--volume",
			f"{data_path}:/usr/app",
			image.reference,
			*command_args,
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		_stdout, stderr = map(lambda io: io.decode().strip(), await process.communicate())
		if(process.returncode != 0):
			raise Exception(f"Failed to run docker container with stderr: {stderr}")


	async def state(self) -> str:
		process = await asyncio.create_subprocess_exec(
			"docker",
			"ps",
			"--all",
			"--filter",
			f"name={self.name}",
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
			self.name,
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		_stdout, stderr = map(lambda io: io.decode().strip(), await process.communicate())
		if(process.returncode != 0):
			raise Exception(f"Failed to stop docker container with stderr: {stderr}")
