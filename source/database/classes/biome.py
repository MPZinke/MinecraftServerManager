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


Biome = TypeVar("Biome")


class Biome:
	def __init__(
		self,
		id: int,
		title: str,
		dimension: str,
		description: str,
	):
		self.id: int = id
		self.title: str = title
		self.dimension: str = dimension
		self.description: str = description


	@staticmethod
	def from_dict(**location_dict: dict) -> Biome:
		return Biome(
			id=location_dict["id"],
			title=location_dict["title"],
			dimension=location_dict["dimension"],
			description=location_dict["description"],
		)
