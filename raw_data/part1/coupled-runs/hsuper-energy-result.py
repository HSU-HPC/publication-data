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
			with open(temp, 'rb') as file:
				try:
					file.seek(-2, os.SEEK_END)
					while file.read(1) != b'\n':
						file.seek(-2, os.SEEK_CUR)
				except OSError:
					file.seek(0)
				last_line = file.readline().decode()
				
				energy = last_line[last_line.find(':') + 1 : last_line.find('kWh')]
				output = output + energy + '\n'
				listFormat = listFormat + str(energy)
				
		listFormat = listFormat + ('' if num == dirSuffixes2[len(dirSuffixes2)-1] else ', ')
	
	listFormat = listFormat + (']\n' if dirSuffix == dirSuffixes[len(dirSuffixes)-1] else '],\n')

listFormat = listFormat + ']'

print(output)
print(listFormat)
