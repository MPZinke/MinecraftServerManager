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


from typing import Tuple, TypeVar


Biome = TypeVar("Biome")
Location = TypeVar("Location")
World = TypeVar("World")


class Location:
	def __init__(
		self,
		id: int,
		title: str,
		location: Tuple[float, float, float],
		dimension: str,
		world: World,
		biome: Biome,
		notes: str,
	):
		self.id: int = id
		self.title: str = title
		self.location: Tuple[float, float, float] = location
		self.dimension: str = dimension
		self.world: World = world
		self.biome: Biome = biome
		self.notes: str = notes


	@staticmethod
	def from_dict(**location_dict: dict) -> Location:
		return Location(
			id=location_dict["id"],
			title=location_dict["title"],
			location=location_dict["location"],
			dimension=location_dict["dimension"],
			world=location_dict["world"],
			biome=location_dict["biome"],
			notes=location_dict["notes"],
		)
