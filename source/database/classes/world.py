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


from datetime import datetime
from io import BytesIO
import os
from pathlib import Path
import shutil
import tarfile
from typing import Optional


import aiofiles


from database.classes.version import Version


class World:
	def __init__(
		self,
		id: int,
		created: datetime,
		data: bytes,
		last_played: datetime,
		name: str,
		notes: str,
		port: Optional[int],
		state: Optional[str],
		version: Version,
	):
		self.id: int = id
		self.created: datetime = created
		self.data: bytes = data
		self.last_played: datetime = last_played
		self.name: str = name
		self.notes: str = notes
		self.port: Optional[int] = port
		self.state: Optional[str] = state
		self.version: Version = version


	@staticmethod
	def from_dict(**world_dict: dict) -> object:
		return World(
			id=world_dict["id"],
			created=world_dict["created"],
			data=world_dict["data"],
			last_played=world_dict["last_played"],
			name=world_dict["name"],
			notes=world_dict["notes"],
			port=world_dict["port"],
			state=world_dict["state"],
			version=world_dict["version"],
		)


	async def read_data(self, data_path: Path) -> None:
		compressed_bytes_file = BytesIO()
		with tarfile.open(fileobj=compressed_bytes_file, mode="w:gz") as compressed_file:
			for root, _, files in os.walk(data_path):
				root_path = Path(root)
				for filename in files:
					filepath = root_path / filename

					async with aiofiles.open(filepath, "rb") as file:
						data = await file.read()

					info = tarfile.TarInfo(name=str(filepath.relative_to(data_path)))
					info.size = len(data)

					compressed_file.addfile(info, BytesIO(data))

		compressed_bytes_file.seek(0)

		self.data = compressed_bytes_file.read()


	async def write_data(self, data_path: Path) -> None:
		if(data_path.exists()):
			shutil.rmtree(data_path)

		data_path.mkdir()

		world_data_file = BytesIO(self.data)
		with tarfile.open(fileobj=world_data_file, mode="r:gz") as tar_file:
			tar_file.extractall(data_path)
