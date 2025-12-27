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


class Version:
	def __init__(
		self,
		id: int,
		released: datetime,
		tag: str,
		title: str,
		url: str,
	):
		self.id: int = id
		self.released: datetime = released
		self.tag: str = tag
		self.title: str = title
		self.url: str = url


	@staticmethod
	def from_dict(**version_dict: dict) -> object:
		return Version(
			id=version_dict["id"],
			released=version_dict["released"],
			tag=version_dict["tag"],
			title=version_dict["title"],
			url=version_dict["url"],
		)
