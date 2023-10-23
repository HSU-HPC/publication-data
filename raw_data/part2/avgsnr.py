import numpy as np
import pandas as pd
import os
import glob
 

offset = 5
cellSize = 5
mddomainSize = 120

firstInnerCellIndex = 1 + 3
lastInnerCellIndex = (mddomainSize//cellSize) - 3

dirprefixes = ['multimd', 'filter']
dirsuffixes1 = [str(2**x) for x in range(0,8)]
dirsuffixes2 = ['_1','_2','_3']

timestepend = 1000
timestepspan = 30
timesteplen = 10
output = ''
listFormat = '[\n'

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
	
print('runtype,num_md_sims,avg_energy,min_energy,max_energy,avg_snr_gain,min_snr_gain,max_snr_gain')
baseCase = 0
for runType in dirprefixes:

	for numMD in dirsuffixes1:
		avgsnr = 0
		ctsnr = 0
		minvalsnr = 0
		maxvalsnr = 0
		firstRunsnr = True
		avgenergy = 0
		ctenergy = 0
		minvalenergy = 0
		maxvalenergy = 0
		firstrunenergy = True
		
		for folder in dirsuffixes2:
			curFolder = '/' + runType + numMD + folder
			path = os.getcwd() + curFolder + '/'
			os.chdir(path)
			#energy
			globobj = glob.glob(path+'output')
			with open(globobj[0], 'rb') as file:
				try:
					file.seek(-2, os.SEEK_END)
					while file.read(1) != b'\n':
						file.seek(-2, os.SEEK_CUR)
				except OSError:
					file.seek(0)
				last_line = file.readline().decode()

				energy = float(last_line[last_line.find(':') + 1 : last_line.find('kWh')])
				avgenergy += energy
				ctenergy += 1
				if firstrunenergy:
					minvalenergy = energy
					maxvalenergy = energy
					firstrunenergy = False
				else:
					minvalenergy = min(minvalenergy,energy)
					maxvalenergy = max(maxvalenergy,energy)

			#snr
			for timestep in range(timestepend-timestepspan+timesteplen, timestepend+timesteplen, timesteplen):
				ans = snr_one_timestep(timestep)
				avgsnr += ans
				ctsnr+=1
				if firstRunsnr:
					minvalsnr = ans
					maxvalsnr = ans
					firstRunsnr = False
				else:
					minvalsnr = min(minvalsnr,ans)
					maxvalsnr = max(maxvalsnr,ans)
			os.chdir('..')
		
		avgsnr /= float(ctsnr)
		if numMD == dirsuffixes1[0] and runType == dirprefixes[0]:
			baseCase = avgsnr
		avgsnr -= baseCase
		minvalsnr -= baseCase
		maxvalsnr -= baseCase
		avgenergy /= float(ctenergy)
		print(f'{runType},{numMD},{avgenergy},{minvalenergy},{maxvalenergy},{avgsnr},{minvalsnr},{maxvalsnr}')

#print(output)
#print('runtype,md_domain_size,avg_energy,min_energy,max_energy,avg_snr_gain,min_snr_gain,max_snr_gain')

