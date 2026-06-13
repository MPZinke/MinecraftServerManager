#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.29                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


import json
from typing import TypeVar


Player = TypeVar("Player")


class Player:
	def __init__(
		self,
		id: int,
		name: str,
		uuid: str,
	):
		self.id: int = id
		self.name: str = name
		self.uuid: str = uuid


	@staticmethod
	def from_dict(**location_dict: dict) -> Player:
		return Player(
			id=location_dict["id"],
			name=location_dict["name"],
			uuid=location_dict["uuid"],
		)


	def __iter__(self) -> dict:
		yield from {"id": self.id, "name": self.name, "uuid": self.uuid}.items()


	def __repr__(self) -> str:
		return str(self)


	def __str__(self) -> str:
		return json.dumps(dict(self), default=str)
