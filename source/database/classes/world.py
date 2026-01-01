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
import getpass
from io import BytesIO
import os
from pathlib import Path
import shutil
import tarfile
from typing import Optional, TypeVar


import aiofiles


from database.classes.version import Version


World = TypeVar("World")


def raise_exception(exception: Exception):
	raise exception


class World:
	WORLDS_DATA_PATH = Path(f"/Users/{os.environ["USER"]}/Gaming/Minecraft/Worlds")


	def __init__(
		self,
		id: int,
		container_id: Optional[str],
		created: datetime,
		data: bytes,
		last_played: datetime,
		name: str,
		notes: str,
		port: Optional[int],
		seed: int,
		state: Optional[str],
		version: Version,
	):
		self.id: int = id
		self.container_id: Optional[str] = container_id
		self.created: datetime = created
		self.data: bytes = data
		self.last_played: datetime = last_played
		self.name: str = name
		self.notes: str = notes
		self.port: Optional[int] = port
		self.seed: Optional[int] = seed
		self.state: Optional[str] = state
		self.version: Version = version

		self._data_path: Path = self.WORLDS_DATA_PATH / f"world-{self.id}"


	@staticmethod
	def from_dict(**world_dict: dict) -> World:
		return World(
			id=world_dict["id"],
			container_id=world_dict["container_id"],
			created=world_dict["created"],
			data=world_dict["data"],
			last_played=world_dict["last_played"],
			name=world_dict["name"],
			notes=world_dict["notes"],
			port=world_dict["port"],
			seed=world_dict["seed"],
			state=world_dict["state"],
			version=world_dict["version"],
		)


	async def read_data(self) -> None:
		compressed_bytes_file = BytesIO()
		with tarfile.open(fileobj=compressed_bytes_file, mode="w:gz") as compressed_file:
			for root, _, files in os.walk(self._data_path, onerror=raise_exception):
				root_path = Path(root)
				for filename in files:
					filepath: Path = root_path / filename
					relative_filepath: Path = filepath.relative_to(self._data_path)

					if(next(iter(relative_filepath.parts), None) in ["libraries", "logs", "versions"]):
						continue

					async with aiofiles.open(filepath, "rb") as file:
						data = await file.read()

					info = tarfile.TarInfo(name=str(relative_filepath))
					info.size = len(data)

					compressed_file.addfile(info, BytesIO(data))

		compressed_bytes_file.seek(0)

		self.data = compressed_bytes_file.read()


	async def write_data(self) -> None:
		if(self._data_path.exists()):
			shutil.rmtree(self._data_path)

		self._data_path.mkdir()

		world_data_file = BytesIO(self.data)
		with tarfile.open(fileobj=world_data_file, mode="r:gz") as tar_file:
			tar_file.extractall(self._data_path)
