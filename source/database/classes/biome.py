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


from typing import TypeVar


from database.classes.biome import Biome
from database.classes.world import World


World = TypeVar("World")


class Biome:
	def __init__(
		self,
		id: int,
		title: str,
		world: str,
		description: str,
	):
		self.id: int = id
		self.title: str = title
		self.world: str = world
		self.description: str = description


	@staticmethod
	def from_dict(**location_dict: dict) -> Biome:
		return Biome(
			id=location_dict["id"],
			title=location_dict["title"],
			world=location_dict["world"],
			description=location_dict["description"],
		)
