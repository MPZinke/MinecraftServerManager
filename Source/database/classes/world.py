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
from typing import Optional


from database.classes.version import Version


class World:
	def __init__(
		self,
		id: int,
		container_id: Optional[str],
		created: datetime,
		data: bytes,
		image_id: Optional[str],
		last_played: datetime,
		port: Optional[int],
		name: str,
		notes: str,
		state: Optional[str],
		version: Version,
	):
		self.id: int = id
		self.container_id: Optional[str] = container_id
		self.created: datetime = created
		self.data: bytes = data
		self.image_id: Optional[str] = image_id
		self.last_played: datetime = last_played
		self.port: Optional[int] = port
		self.name: str = name
		self.notes: str = notes
		self.state: Optional[str] = state
		self.version: Version = version


	@staticmethod
	def from_dict(**world_dict: dict) -> object:
		return World(
			id=world_dict["id"],
			container_id=world_dict["container_id"],
			created=world_dict["created"],
			data=world_dict["data"],
			image_id=world_dict["image_id"],
			last_played=world_dict["last_played"],
			port=world_dict["port"],
			name=world_dict["name"],
			notes=world_dict["notes"],
			state=world_dict["state"],
			version=world_dict["version"],
		)


	def start(self):
		from database.queries.worlds import set_world_container, set_world_image, set_world_state
		from docker import Container, Image

		self.state = "building"
		set_world_state(self)

		try:
			image = Image.build(self)

		except Exception as error:
			self.state = "clean"
			set_world_state(self)
			raise

		self.image_id = image.id
		set_world_image(self)

		try:
			container = Container.run(image)

		except Exception as error:
			self.state = "clean"
			set_world_state(self)
			raise

		self.container_id = container.id
		self.port = container.port
		set_world_container(self)


	def stop(self):
		from database.queries.worlds import set_world_stop
		from docker import Container, Image

		container = Container(self.container_id, Image(self.image_id), self.port)
		self.data = container.stop()
		set_world_stop(self)
		container.image.remove()
