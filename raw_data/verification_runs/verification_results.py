#! /usr/bin/env python3

import numpy as np
import pandas as pd
import os
import glob

offset = 5
cellSize = 5

timestepend = 100
timestepspan = 30
timesteplen = 10

volumes = [80, 100, 160]
mds = [1, 36, 72, 108, 144]

def get_cell_midpoint(cellNum):
	return offset + ((cellNum-1)*cellSize)+(cellSize/2.0)


def couette_analytic(z, t):
	""" Analytic Couette startup equation
	"""
	u_w = 1.5
	H = 200.
	v = 2.14 / .813037037
 
	k_sum = 0
	for k in range(1, 1001):
		k_sum += (1.0/k) * np.sin(k*np.pi*z/H) * \
		np.exp( (-1.0 * (k*k) * (np.pi*np.pi) * v * t / (H*H)))
 
	k_sum *= 2.0 * u_w/np.pi
 
	return u_w * (1.0-(z/H)) - k_sum

def loadDataFromNodeCsv(csv_file,t, mddomainSize):
	""" Get CSV data from one cycle and compute
	the SNR from this timestep's solution
	"""
	firstInnerCellIndex = 1 + 3
	lastInnerCellIndex = (mddomainSize//cellSize) - 3
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
 
def snr_one_timestep(path, t, v):
	""" Find SNR from analytical Couette profile and velocities
	of the inner cells from one coupling cycle
	"""
	csv_file = path + "CouetteAvgMultiMDCells_0_" + str(t) + ".csv"
	results = loadDataFromNodeCsv(csv_file,t/2, v)
	#print(str(results) + " dB at t=" + str(t))
	return results

print('md_size,num_md_sims,snr_gain,energy,num_eq_timesteps')
baseCase = 0
for volume in volumes:

	for md in mds:
		curFolder = '/V' + str(volume) + '/M' + str(md)
		path = os.getcwd() + curFolder + '/'
		if volume == 160 and md == 144:
			path = os.getcwd() + curFolder + '_stacked/'
		#energy
		globobj = glob.glob(path+'output')
		if not (len(globobj) == 1):
			print(f'{volume},{md},error,error,5000')
			continue
		with open(globobj[0], 'rb') as file:
			try:
				file.seek(-2, os.SEEK_END)
				while file.read(1) != b'\n':
					file.seek(-2, os.SEEK_CUR)
			except OSError:
				file.seek(0)
			last_line = file.readline().decode()

			energy = float(last_line[last_line.find(':') + 1 : last_line.find('kWh')])
		#snr
		snr = snr_one_timestep(path, timestepend, volume)
		if md == mds[0]: 
			baseCase = snr
		snr -= baseCase
		print(f'{volume},{md},{snr},{energy},5000')

#print(output)
#print('runtype,md_domain_size,avg_energy,min_energy,max_energy,avg_snr_gain,min_snr_gain,max_snr_gain')

