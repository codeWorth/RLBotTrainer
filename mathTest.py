import numpy as np
from paginateData import DataPagination
import argparse
from matplotlib import pyplot as plt

positionScale = np.array([4096*2, 5120*2, 2044], dtype=">f4")
ballVScale = 6000*2
playerVScale = 2300*2
angularVScale = 5.5*2
np.set_printoptions(precision=6, suppress=True)

def denormX(x):
	return (x - 0.5) * positionScale[0]

def denormY(y):
	return (y - 0.5) * positionScale[1]

def denormZ(z):
	return z * positionScale[2]

def denormBallV(v):
	return (v - 0.5) * ballVScale

def denormPlayerV(v):
	return (v - 0.5) * playerVScale

def denormAngularV(v):
	return (v - 0.5) * angularVScale

def denormPitch(pitch):
	return (pitch - 0.5) * np.pi

def denormYaw(yaw):
	return (yaw - 0.5) * np.pi * 2

def denormRoll(roll):
	return (roll - 0.5) * np.pi * 2

def controlInput(k):
	return (k - 0.5) * 2

def denormFrames(frames, playerCount):
	frames[:,1:12] -= 0.5
	frames[:,3] += 0.5
	frames[:,1:4] *= positionScale
	frames[:,4:7] *= ballVScale
	frames[:,7:12] *= 2

	for i in range(playerCount):
		j = 15 + i * 15
		frames[:,j+1:j+13] -= 0.5
		frames[:,j+1:j+4] *= positionScale
		frames[:,j+4:j+7] *= playerVScale
		frames[:,j+7] *= np.pi
		frames[:,j+8:j+10] *= np.pi*2
		frames[:,j+10:j+13] *= angularVScale
		frames[:,j+14] *= 100

def multQuats(a, b, out):
	out[0] = a[0]*b[0] - a[1]*b[1] - a[2]*b[2] - a[3]*b[3]
	out[1] = a[0]*b[1] + a[1]*b[0] + a[2]*b[3] - a[3]*b[2]
	out[2] = a[0]*b[2] + a[2]*b[0] + a[3]*b[1] - a[1]*b[3]
	out[3] = a[0]*b[3] + a[3]*b[0] + a[1]*b[2] - a[2]*b[1]

def eulersToQuats(ys, ps, rs):
	cy = np.cos(ys/2)
	cp = np.cos(ps/2)
	cr = np.cos(rs/2)
	sy = np.sin(ys/2)
	sp = np.sin(ps/2)
	sr = np.sin(rs/2)
	out = np.empty((ys.shape[0], 4), dtype=ys.dtype)
	out[:,0] = cr*cp*cy + sr*sp*sy
	out[:,1] = sr*cp*cy - cr*sp*sy
	out[:,2] = cr*sp*cy + sr*cp*sy
	out[:,3] = cr*cp*sy - sr*sp*cy
	return out

def angularsToQuats(vs):
	k2s = np.sum(np.square(vs), axis=1)
	ks = np.sqrt(k2s)
	k2s[k2s == 0] = 1 # avoid divide by zero errors
	out = np.empty((vs.shape[0], 4), dtype=vs.dtype)
	out[:,0] = np.cos(ks/2)
	norms = np.sqrt((1 - np.square(out[:,0])) / k2s)
	out[:,1:4] = vs[:,0:3] * norms[:,None]
	return out

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Paginates gzip compressed training data.")
	parser.add_argument("input", type=str, help="The compressed .gz file or an uncompressed file containing training data.")
	args = parser.parse_args()

	data = DataPagination(args.input)
	while data.hasPage():
		frames = data.nextPage().copy()
		denormFrames(frames, data.playerCount)
		goals = np.argwhere(frames[:,0] < 0)[:,0]
		for i in range(goals.shape[0]):
			if i < 1:
				continue

			start = goals[i]+1
			if i < goals.shape[0] - 1:
				end = goals[i+1]
			else:
				end = frames.shape[0]

			subFrames = frames[start:end]
			time = np.cumsum(subFrames[:,0])

			origAngs = subFrames[:,22:25].copy() # pitch, yaw, roll
			angVels = subFrames[:,25:28].copy() # roll, pitch, yaw
			origAngs[:,0] *= -1
			origAngs[:,2] *= -1
			origQuats = eulersToQuats(origAngs[:,1], origAngs[:,0], origAngs[:,2])
			velQuats = angularsToQuats(angVels * subFrames[:,0:1])

			n = 2345
			predQuats = np.empty_like(origQuats)
			predQuats[:n] = origQuats[:n]
			for i in range(n, origQuats.shape[0]):
				multQuats(velQuats[i-1], predQuats[i-1], predQuats[i])

			print("pitch, yaw, roll", origAngs[n-1])
			print("dx dy dz", angVels[n-1], "*", subFrames[n-1,0])
			print("angle quat (wxyz)", origQuats[n-1])
			print("vel quat (wxyz)", velQuats[n-1])
			print("next")
			print("pitch, yaw, roll", origAngs[n])
			print("dx dy dz", angVels[n], "*", subFrames[n,0])
			print("angle quat (wxyz)", origQuats[n])
			print("vel quat (wxyz)", velQuats[n])
			print("predicted")
			print("angle quat (wxyz)", predQuats[n])

			# error = 2 * np.arccos(np.abs(np.sum(origQuats * predQuats, axis=1)))
			# plt.plot(error)
			# plt.plot(np.abs(origAngs[:,2]) >= np.pi/2)
			# plt.show()

			# plt.plot(time, origAngs[:,2])
			# plt.plot(time, angVels)
			# plt.legend(["roll", "upsidedown", "error", "x", "y", "z"])


			# angRots = np.sqrt(np.sum(np.square(angVels), axis=1))
			# k1s = np.sin(angRots)
			# k2s = 1 - np.cos(angRots)
			# i = 1
			# if angRots[i] == 0:
			# 	predAngs[i] = predAngs[i-1]
			# else:
			# 	k1 = k1s[i-1]
			# 	k2 = k2s[i-1]
			# 	u = angVels[i-1] / angRots[i-1]

			# 	r31 = k1*u[1] + k2*u[0]*u[2]
			# 	deltaPitch = -np.arcsin(r31)

			# 	r32 = k1*u[0] + k2*u[1]*u[2]
			# 	r33 = 1 - k2*(u[0]*u[0] + u[1]*u[1])
			# 	r21 = k1*u[2] + k2*u[0]*u[1]
			# 	r11 = 1 - k2*(u[1]*u[1] + u[2]*u[2])
				
			# 	if np.cos(deltaPitch) > 0:
			# 		deltaYaw = np.arctan2(r21, r11)
			# 		deltaRoll = np.arctan2(r32, r33)
			# 	else:
			# 		deltaYaw = np.arctan2(-r21, -r11)
			# 		deltaRoll = np.arctan2(-r32, -r33)

			exit()