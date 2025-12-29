#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.28                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


from io import BytesIO
import os
from pathlib import Path
import sys
import tarfile


def read_data(data_path: Path) -> None:
	compressed_bytes_file = BytesIO()

	with tarfile.open(fileobj=compressed_bytes_file, mode="w:gz") as compressed_file:
		for root, _, files in os.walk(data_path):
			root_path = Path(root)
			for filename in files:
				filepath = root_path / filename
				with open(filepath, "rb") as file:
					data: bytes = file.read()

				info = tarfile.TarInfo(name=str(filepath.relative_to(data_path)))
				info.size = len(data)
				compressed_file.addfile(info, BytesIO(data))

	compressed_bytes_file.seek(0)
	return compressed_bytes_file.read()


def main():
	path = Path(sys.argv[1])
	data: bytes = read_data(path)
	print(f"'\\x{data.hex()}'::BYTEA")


main()
