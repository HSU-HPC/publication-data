import seaborn as sns
import sys
import numpy as np
import pandas as pd
import matplotlib as mpl
#mpl.use('Agg')
#mpl.rcParams['lines.linewidth'] = 2
from matplotlib import pyplot as plt

counter = 0
offset = 5
x_step = 5
x = np.arange(x_step/2,100,x_step)

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

def loadAvgDataFromNodeCsv(csv_file):
	""" Get CSV data from one cycle and compute
	the average velocity per layer of cells in z-direction
	"""
	# load data in pandas DataFrame
	df = pd.read_csv(csv_file, sep=";", header=None)
 
	# get Avg x velocity per z layer
	avgVelocities = []
	for i in range(4,22):
		avg = 0
		mass = 0
		j = 0
		for _,row in df[df[2] == i].iterrows():
			avg += (row[3])
			break
		#if df[df[2] == i].shape[0] > 0:
			#avgVelocities.append(avg/df[df[2] == i].shape[0])
		avgVelocities.append(avg)
	return avgVelocities
 
def plot_one_timestep(t, ax):
	""" Plot analytical Couette profile and velocities
	of the inner cells from one coupling cycle
	"""
	global simulations
	global offset
	global counter
	csv_file = "CouetteAvgMultiMDCells_0_" + str(t) + ".csv"
	results = loadAvgDataFromNodeCsv(csv_file)
	print(results)
	z = np.linspace(0,200,num=81)
	y = couette_analytic(z, t/2) #multiply MD timestep by number of MD per coupling, multiply that factor with t here
	ax.plot(z, y, "-", color=sns.color_palette(my_map,10)[counter], linewidth=1)
	ax.plot(np.linspace(15+2.5+offset, 15+2.5+85+offset, num=18), results, "x", color=sns.color_palette(my_map,10)[counter], label="Step "+str(t) ,markersize=7)

	#f = np.genfromtxt("velocity_"+str(t)+".txt", usecols=(0), delimiter=',', dtype="float")
	#x_help = [0,1,2,3,10,11,12,13,14,15,16,17,18,19]
	#plt.plot(x[x_help], f, linestyle ='none', marker='o', color=sns.color_palette(my_map,10)[counter], markersize=7)

	counter = counter + 1
 
#plt.style.use("ggplot")
plt.figure(figsize=(5.44,4 * 0.8))
plt.rcParams['font.size'] = 15
plt.rcParams["savefig.dpi"] = 250
plt.rcParams["savefig.pad_inches"]=0.05
my_map = "Paired"
fig, ax = plt.subplots()
	 
plot_one_timestep(30, ax)
plot_one_timestep(50, ax)
plot_one_timestep(80, ax)
plot_one_timestep(130, ax)
plot_one_timestep(250, ax)
plot_one_timestep(500, ax)
plot_one_timestep(750, ax)
plot_one_timestep(1000, ax)

plt.xlabel('z')
plt.ylabel('u')
plt.legend()
plt.xlim(0,200)
fig_width, fig_height = plt.gcf().get_size_inches()
print(fig_width, fig_height)
fig.set_size_inches(7.5, 5, forward=True)
plt.title("MultiMD - 1 Instance")
plt.savefig("mmd72.png", format="png", bbox_inches='tight')
plt.show()
 
exit(0)
