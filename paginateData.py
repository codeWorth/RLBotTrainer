import argparse, os, subprocess
import numpy as np
from matplotlib import pyplot as plt

import struct

def floatsPerFrame(playerCount):
	return 15 + 15 * playerCount

class DataPagination:
	def __init__(self, path, bytesPerPage=200000000, verbose=False): # 200 mb per page (ish, will be slightly decreased)
		self.verbose = verbose
		self.dtype = ">f4"

		if path.split(".")[-1] == "gz":
			self.log("Decompressing", path, "...")
			path = path.split(".")[0]
			if os.path.exists(path):
				self.log("Existing decompressed file exists at", path)
			else:
				subprocess.run(["gzip.exe", "-kqd", path + ".gz"])
				self.log("Finished decompress")

		self.file = open(path, "rb")
		headerBytes = self.file.read(8) # 2 floats
		try:
			headerFloats = np.frombuffer(headerBytes, dtype=self.dtype, count=2)
			self.playerCount = int(headerFloats[0])
			self.playerIndex = int(headerFloats[1])
			self.log("Header found", self.playerCount, "players")
			self.log("This player is index", self.playerIndex)
		except ValueError as error:
			self.log("File does not contain header")
			raise error

		self.floatsPerFrame = floatsPerFrame(self.playerCount)
		self.bytesPerFrame = self.floatsPerFrame * 4
		self.framesPerPage = bytesPerPage // self.bytesPerFrame
		bytesPerPage = self.bytesPerFrame * self.framesPerPage
		self.bytesPerPage = bytesPerPage

		print(self.floatsPerFrame, "floats per frame")
		print(self.bytesPerPage, "bytes per page")
		print(self.framesPerPage, "frames per page")

		self._hasPage = True

	def __del__(self):
		self.log("Closing file")
		self.file.close()

	def log(self, *message):
		if (self.verbose):
			print(*message)

	def hasPage(self):
		return self._hasPage

	def nextPage(self):
		data = self.file.read(self.bytesPerPage)

		dataBytes = len(data)
		if (dataBytes % self.bytesPerFrame) != 0:
			oldBytes = dataBytes
			dataBytes = (dataBytes // self.bytesPerFrame) * self.bytesPerFrame
			self.log("Reading page results in partial frame, will truncate extra", (oldBytes-dataBytes), "bytes")
			self.log("Reading", dataBytes, "bytes instead of", oldBytes, "bytes")

		if dataBytes < self.bytesPerPage:
			self._hasPage = False
			self.file.close()

		framesInData = dataBytes // self.bytesPerFrame
		floatsInData = dataBytes // 4

		return np.frombuffer(data, dtype=self.dtype, count=floatsInData).reshape(framesInData, self.floatsPerFrame)


def cleanZeros(frames):
	return frames[frames[:,0] > 0]

def cleanNaNs(frames):
	return frames[np.argwhere((~np.isnan(frames)).any(axis=1))[:,0]]

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Paginates gzip compressed training data.")
	parser.add_argument("input", type=str, help="The compressed .gz file or an uncompressed file containing training data.")
	args = parser.parse_args()

	data = DataPagination(args.input, verbose=True)
	while data.hasPage():
		frames = data.nextPage()
		plt.plot(frames[:, 3])
		plt.show()

	# with open(args.input.split(".")[0]+"-fixed", "w+b") as f:
	# 	f.write(struct.pack(">f", 4.0))
	# 	f.write(struct.pack(">f", 0.0))
	# 	f.write(frames.tobytes())