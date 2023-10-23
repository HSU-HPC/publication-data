#!/usr/bin/env python3

import shutil
import os
import subprocess
import glob

dirSuffixes0 = ["md"]
dirSuffixes1 = [str(x*30) for x in range(1,8)]
dirSuffixes2 = [str(x) for x in range(1,4)]
dirSuffixes = [x+y for x in dirSuffixes0 for y in dirSuffixes1]

output = ''
listFormat = '[\n'

for dirSuffix in dirSuffixes:

	listFormat = listFormat + '[ '

	for num in dirSuffixes2:

		curFolder = '/' + dirSuffix + '_' + num
		output = output + curFolder + '\t'
		path = os.getcwd() + curFolder + '/' + 'output'
		globobj = glob.glob(path)
		if not (len(globobj) == 1):
			output = output + 'globlen = ' + str(len(globobj)) + ' error \n'
			listFormat = listFormat + 'None'
		else:
			temp = globobj[0]
			# Read energy consumption from last line
			with open(temp, 'rb') as file:
				try:
					file.seek(-2, os.SEEK_END)
					while file.read(1) != b'\n':
						file.seek(-2, os.SEEK_CUR)
				except OSError:
					file.seek(0)
				last_line = file.readline().decode()
				
				energy = last_line[last_line.find(':') + 1 : last_line.find('kWh')]
				output += energy + '\t'
				listFormat = listFormat + str(energy)

			# Read mamico coupling time consumption from last line
			mamico_coupling_time = 'nan'
			cpu_time = 'nan'
			wall_time = 'nan'
			with open(temp, 'r') as file:
				for line in file:
					if 'Plugin MamicoCoupling' in line:
						mamico_coupling_time = line.split(': ')[-1][:-4]
					elif 'Used CPU time' in line:
						cpu_time = line.split(': ')[1].split('(')[0].strip()
					elif 'Used walltime' in line:
						wall_time = line.split(': ')[1].split('(')[0].strip()
			output += mamico_coupling_time + '\t' + cpu_time + '\t' + wall_time + '\n'
				
		listFormat = listFormat + ('' if num == dirSuffixes2[len(dirSuffixes2)-1] else ', ')
	
	listFormat = listFormat + (']\n' if dirSuffix == dirSuffixes[len(dirSuffixes)-1] else '],\n')

listFormat = listFormat + ']'

#print(output)
#print(listFormat)

# Output as CSV
print('filename,md_domain_size,cpu_time,wall_time,energy_consumption_kWh,mamico_coupling_time')
for line in output.split('\n'):
	if len(line.strip()) == 0:
		break
	output_folder, energy_consumption_kWh, mamico_coupling_time,cpu_time,wall_time = line.split('\t')
	domain_size = output_folder.split('_')[0][3:]
	print(f'{output_folder.strip()}/output,{domain_size},{cpu_time},{wall_time},{energy_consumption_kWh.strip()},{mamico_coupling_time}')
