import numpy as np
import pandas as pd
import os
 

offset = 5
cellSize = 5
mddomainSize = 60

firstInnerCellIndex = 1 + 3
lastInnerCellIndex = (mddomainSize//cellSize) - 3

dirprefixes = ['multimd', 'filter']
dirsuffixes1 = [str(2**x) for x in range(0,8)]
dirsuffixes2 = ['','_2','_3']

timestep = 30

output = ''
listFormat = '[\n'

def get_cell_midpoint(cellNum):
	return offset + ((cellNum-1)*cellSize)+(cellSize/2.0)


def couette_analytic(z, t):
	""" Analytic Couette startup equation
	"""
	u_w = 1.5
	H = 100.
	v = 2.14 / .813037037
 
	k_sum = 0
	for k in range(1, 1001):
		k_sum += (1.0/k) * np.sin(k*np.pi*z/H) * \
		np.exp( (-1.0 * (k*k) * (np.pi*np.pi) * v * t / (H*H)))
 
	k_sum *= 2.0 * u_w/np.pi
 
	return u_w * (1.0-(z/H)) - k_sum

def loadDataFromNodeCsv(csv_file,t):
	""" Get CSV data from one cycle and compute
	the SNR from this timestep's solution
	"""
	# load data in pandas DataFrame
	df = pd.read_csv(csv_file, sep=";", header=None)
 
	# get Avg x velocity per z layer
	snr_sumSig = 0
	snr_sumNoise = 0
	for i in range(firstInnerCellIndex,lastInnerCellIndex+1):
		z = get_cell_midpoint(i)
		sig = couette_analytic(z,t)
		
		for _,row in df[df[2] == i].iterrows():
			#print("i="+str(i)+" sig="+str(sig)+" z="+str(z)+" value="+str(row[3]))
			snr_sumNoise += ((row[3]-sig)*(row[3]-sig))
			snr_sumSig += sig*sig
			#break
		
		
	return 10 * np.log10(snr_sumSig/snr_sumNoise)
 
def snr_one_timestep(t):
	""" Find SNR from analytical Couette profile and velocities
	of the inner cells from one coupling cycle
	"""
	csv_file = "CouetteAvgMultiMDCells_0_" + str(t) + ".csv"
	results = loadDataFromNodeCsv(csv_file,t/2)
	#print(str(results) + " dB at t=" + str(t))
	return results
	

baseCase = 0
for runType in dirprefixes:

	for numMD in dirsuffixes1:
		ans = 0
		
		for folder in dirsuffixes2:
			curFolder = '/' + runType + numMD + folder
			path = os.getcwd() + curFolder + '/'
			os.chdir(path)
			ans += snr_one_timestep(timestep)
			os.chdir('..')
		
		ans /= 3.0
		if numMD == dirsuffixes1[0] and runType == dirprefixes[0]:
			baseCase = ans
		ans -= baseCase
		output = output + runType + numMD + '\t' + str(ans) + '\n'

print(output)

exit(0)
