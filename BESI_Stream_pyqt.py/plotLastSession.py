# Performs some processing on sensor data files,saves the files, and plots the data 
# File name is the sensor ID + the date it was recorded
from dataPreprocessing import *
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from plotSavedAccel import plotAccel, calibrateMagnitude
from plotSavedLight import plotLight
from plotSavedNoise import plotNoise
from plotSavedTemp import plotTemp, lowPassFilter

#raw data files are named based on the socket port used to get the data from the BBB
basePort = PORT1


rawAccelFile = open("accel" + "{}".format(basePort), "r")
rawLightFile = open("light" + "{}".format(basePort + 1), "r")
rawNoiseFile = open("sound" + "{}".format(basePort + 2), "r")
rawTempFile = open("temp" + "{}".format(basePort + 3), "r")

# processing is mostly creating timestamps relative to he start of the data collection
# these functions produce files name sensor ID + date
fname1, t = processAccel(rawAccelFile)
fname2 = processLight(rawLightFile)
fname3 = processSound(rawNoiseFile)
fname4 = processTemp(rawTempFile)

print fname3

rawAccelFile.close()
rawLightFile.close()
rawNoiseFile.close()
rawTempFile.close()

# open processed data files
accelProcFile = open(fname1, "r")
lightProcFile = open(fname2, "r")
noiseProcFile = open(fname3, "r")
tempProcFile = open(fname4, "r")

"""
# open processed data files
accelProcFile = open("Accelerometer2015-06-03", "r")
lightProcFile = open("Ambient Light2015-06-03", "r")
noiseProcFile = open("Ambient Noise2015-06-03", "r")
tempProcFile = open("Temperature2015-06-03", "r")
"""

# create time series of data from each file
t_data, x_data, y_data, z_data = plotAccel(accelProcFile)
tlight_data, light_data = plotLight(lightProcFile)
tnoise_data, noise_data = plotNoise(noiseProcFile)
tTemp_data, temp_data = plotTemp(tempProcFile)

app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)
           
win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('BESI Data from Last Saved Session')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Accel Plot
p1 = win.addPlot(title="Accelerometer Data")
p1.setLabel('left', "Uncalibrated Accelerometer", units='')
p1.setLabel('bottom', "Time", units='s')
p1.plot(t_data, calibrateMagnitude(t, x_data, y_data, z_data), pen=(255,0,0), name="Accel curve")
#p1.plot(t_data, x_data, pen=(0,255,0), name="X curve")
#p1.plot(t_data, y_data, pen=(0,0,255), name="Y curve")
#p1.plot(t_data, z_data, pen=(255,0,255), name="Z curve")

# Light Plot
p2 = win.addPlot(title="Ambient Light Data")
p2.setLabel('left', "Light Level", units='Lux')
p2.setLabel('bottom', "Time", units='s')
p2.plot(tlight_data, light_data, pen=(0,255,0), name="Filtered")

win.nextRow()

# Plot Noise
p3 = win.addPlot(title="Ambient Noise Data")
p3.setLabel('left', "Noise Amplitude over 0.1s of data", units='V')
p3.setLabel('bottom', "Time", units='s')
p3.plot(tnoise_data, noise_data, pen=(0,255,0), name="Filtered")

# plot temperature
p4 = win.addPlot(title="Temperature Data")
p4.setLabel('left', "Temperature (raw and LPF)", units='Degree F')
p4.setLabel('bottom', "Time", units='s')
p4.plot(tTemp_data, lowPassFilter(temp_data), pen=(0,255,0), name="Filtered")
#p4.plot(tTemp_data, temp_data, pen=(0,0,255), name="Unfiltered")

print "Accel Duration: {}".format(t_data[-1])
print "Light Duration: {}".format(tlight_data[-1])
print "Noise Duration: {}".format(tnoise_data[-1])
print "Temp Duration: {}".format(tTemp_data[-1])

accelProcFile.close()
lightProcFile.close()
noiseProcFile.close()
tempProcFile.close()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()