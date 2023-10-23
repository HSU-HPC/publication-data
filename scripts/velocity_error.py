#! /usr/bin/env python3

# From ErrorEstimation.h in Mamico
import math

def getErrorVelocity(numberOfSamples, velocity, temperature, numberOfParticle, particleMass):
	error = 1 / (velocitySNR(velocity, temperature, numberOfParticle, particleMass) * math.sqrt(numberOfSamples))
	return error

def velocitySNR(velocity, temperature, numberOfParticle, particleMass):
	return velocity / velocityFluctuation(temperature, numberOfParticle, particleMass)


def velocityFluctuation(temperature, numberOfParticle, particleMass):
	_k = 1.0
	return math.sqrt(_k * temperature / particleMass / numberOfParticle)


velocity = 1 #absolute error
numberOfSamples = [1,2,4,8,16,32,64,128]
temperature = 1.1
particleMass = 1.0
#numberOfParticle = 171500 / ((60/5)**3)#md60, density 0.81, taken from ls1
#numberOfParticle = 1401611 / ((120/5) ** 3)#md120, density 0.81, taken from ls1
numberOfParticle = 4764064 / ((180/5) ** 3)#md180, density 0.81, taken from ls1
print('num_md_sims,abs_vel_error')
for val in numberOfSamples:
	print(f'{val},{getErrorVelocity(val,velocity,temperature,numberOfParticle,particleMass)}')
