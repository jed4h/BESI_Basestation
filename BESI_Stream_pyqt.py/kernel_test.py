from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import math
from processLight import plotLight
from processTemp import plotTemp, lowPassFilter
from processNoise import plotNoise
from BikeCadence import *
from processAccel import plotAccel

#windowSize = 100
#threshold = 0.64
#outlierHigh =  74
#outlierLow = -100

#QtGui.QApplication.setGraphicsSystem('raster')
#app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

# if the file = None, the raw data file was empty

# calculates the probability that sample occurred given the history of sensor values in previouData
def GaussianKernel(previousData, sample):
    ysample = 0.0
    for value in previousData:
        ysample = ysample + (1.0/(math.sqrt(2*math.pi)))*math.exp(-0.5 * ((sample-value)**2))
        
    return ysample/len(previousData)

# calculates the PDF for the data points given in samples by computing the probability at each value in x
def calculatePDF(x, samples):
    y = [0]*len(x)
    for value in samples:
        for i in range(len(x)):
            y[i] = y[i] + (1.0/(math.sqrt(2*math.pi)))*math.exp(-0.5 * ((x[i]-value)**2))
        for i in range(len(y)):
            y[i] = y[i]*(1.0/len(samples))
            
    return y 

#calculates if the last point in samples is an outlier based on the previous windowSize - 1 points
def isOutlier(samples, windowSize):
    if (len(samples) < windowSize):
        return 0.6
    else:
        return (1 - GaussianKernel(samples[-windowSize:-2], samples[-1]))

# calculates the probability of each data point in an array occurring based on the previous samples in windowSize and returns the result in prob
# based on prob and a given threshold, the data points that are outliers are determined and marked as outLierHigh
def sampleProbability(samples, windowSize, threshold, outlierHigh, outlierLow):
    prob = [0.6]*windowSize
    outliers = []
    for i in range(len(samples) - windowSize):
        prob.append(1 - GaussianKernel(samples[i:i + windowSize-1], samples[i + windowSize]))
        
    for i in range(len(prob)):
        if prob[i] > threshold:
            outliers.append(outlierHigh)
        else:
            outliers.append(outlierLow)
            
    return prob, outliers

# scales data to the range -3 to 3
def scaleData(data):
    scaledData = []
    scale = 6.0/(max(data) - min(data))
    offset = (max(data) - min(data))/2.0 + min(data)
    for i in range(len(data)):
        scaledData.append((data[i] - offset) * scale)
    return scaledData

"""
lightProcFile = open("data/Ambient Light2015-06-09_10-28", "r")
tlight_data, light_data = plotLight(lightProcFile)
tempProcFile = open("data/Temperature2015-07-24_16-09", "r")
tTemp_data, temp_data = plotTemp(tempProcFile)

noiseProcFile = open("data/Ambient Noise2015-06-09_10-28", "r")
tnoise_data, noise_data = plotNoise(noiseProcFile)

accelProcFile = open("data/Accelerometer2015-05-28_V2", "r")
t_data, x_data, y_data, z_data = plotAccel(accelProcFile)

#Bike Cadence
fileName = "data/Accelerometer2015-06-12_V2"
time, x_bike, y_bike, z_bike, duration = readData(fileName)
count, intervals = peakDetection(lowPassFilter(x_bike), lowPassFilter(y_bike), time)
mainterval = movingAvg(intervals)
masamples = scaleData(mainterval)


noise_per_second = []
for i in range(len(noise_data)/100):
    avg = 0
    for j in range(100):
        avg = avg + noise_data[i * 100 + j]
        
    noise_per_second.append(avg/200.0)

samples = noise_per_second       

scaled_light = scaleData(light_data)
scaled_temp = scaleData(temp_data)
    
samples1 = scaled_light[:len(samples)/5]
samples2 = scaled_light[len(samples)/5:2*len(samples)/5]
samples3 = scaled_light[2*len(samples)/5:3*len(samples)/5]
samples4 = scaled_light[3*len(samples)/5:4*len(samples)/5]
samples5 = scaled_light[4*len(samples)/5:]

x = [i/100.0 - 3 for i in range(600)]

y = calculatePDF(x, samples)
y1 = calculatePDF(x, samples1)
y1 = calculatePDF(x, samples2)
y1 = calculatePDF(x, samples3)
y1 = calculatePDF(x, samples4)
y1 = calculatePDF(x, samples5)


win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)




#analyze using a sliding window
prob, outliers = sampleProbability(lowPassFilter(temp_data), windowSize, threshold, outlierHigh, outlierLow)     
prob2, outliers2 = sampleProbability(samples, windowSize, threshold, outlierHigh, outlierLow)
maprob, maoutliers = sampleProbability(masamples, windowSize, threshold, outlierHigh, outlierLow)


  
thresholdPlot = [threshold]*len(prob)

#p1 = win.addPlot(title="Outlier probability")
#p1.setLabel('left', "1 - Probability of Occurrence", )
#p1.setLabel('bottom', "Time (s)", )
#p1.plot(prob, pen=(255,255,255), name="X curve") 
#p1.plot(threshold, pen=(0,255,255), name="X curve") 


p3 = win.addPlot(title="Outlier Probability")
p3.setLabel('left', "1 - Probability of Occurrence")
p3.setLabel('bottom', "Time (s)", )
p3.plot(prob, pen=(255,255,255), name="X curve") # yellow
p3.plot(thresholdPlot, pen=(0,255,255), name="X curve") 

p2 = win.addPlot(title="Bike Cadence (5-point moving average)")
p2.setLabel('left', "Stationary Bike RPMs")
p2.setLabel('bottom', "Time (s)", )
p2.plot(temp_data, pen=(255,0,255), name="X curve") # green
p2.plot(outliers, pen=None, symbol='o', symbolPen=None, symbolSize=5, symbolBrush=(0, 255, 255, 255)) # red
#p2.plot(maprob, pen=None, symbol='o', symbolPen=None, symbolSize=3, symbolBrush=(255, 0, 0, 255)) # red

#win.nextRow()





#p4 = win.addPlot(title="Basic array plotting")
#p4.plot(temp_data[:17500], light_data[:17500], pen=None, symbol='o', symbolPen=None, symbolSize=2, symbolBrush=(255, 0, 0, 255))
#p4.plot(maprob, pen=(0,255,0), name="X curve") # yellow
'''
p2 = win.addPlot(title="Light Level (Lux)")
p2.setLabel('left', "Lux", )
p2.setLabel('bottom', "Time (s)", )
p2.plot(light_data, pen=(255,255,255), name="X curve") # green
p1 = win.addPlot(title="Light PDF")
p1.setLabel('left', "Probability", )
p1.setLabel('bottom', "Lux scaled to (-3, 3)", )
p1.plot(x,y, pen=(255,255,255), name="X curve") # green
'''
#p1.plot(x,y2, pen=(255,255,0), name="X curve") # yellow
#p1.plot(x,y3, pen=(0,0,255), name="X curve") # Blue
#p1.plot(x,y4, pen=(255,0,0), name="X curve") # red
#p1.plot(x,y5, pen=(255,0,255), name="X curve") # purple



## Start Qt event loop unless running iyn interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        
"""