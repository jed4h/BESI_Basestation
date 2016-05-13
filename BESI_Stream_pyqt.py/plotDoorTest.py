from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from processAccel import plotAccel
from processLight import plotLight
from processNoise import plotNoise
from processTemp import plotTemp, lowPassFilter
from processDoor import plotDoor
import Tkinter as tk
import tkFileDialog
from os import listdir
from localizationUtils import *


tdoor_data = []
door1_data_unfiltered = []
door2_data_unfiltered = []
door_diff = []
door1_deriv = []
door2_deriv = []
diff_deriv = []

root = tk.Tk()
root.withdraw()

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

downsampleRate = 1

window_size = 10
avgRange = 200

accelLastTime = 0
startDatetime = "2016-04-17_11-22.txt"
peakThreshold = 1
startDate = startDatetime


deployID = 16
relayID = 10009

basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayID) + "/"

#for fileName in  listdir(basePath + "Door"):
doorProcFile = open(basePath + "Door/" + "Door Sensor_Synched" + startDatetime, "r")
tdoor_data_tmp, door1_data_tmp, door2_data_tmp = plotDoor(doorProcFile)

for tValue in tdoor_data_tmp:
    tdoor_data.append(tValue)

for doorValue in door1_data_tmp:
    door1_data_unfiltered.append(doorValue)
    
for doorValue in door2_data_tmp:
    door2_data_unfiltered.append(doorValue)
    
dsData = getDSEvents(deployID, relayID, startDate, peakThreshold, window_size, avgRange, 1,2,3)

print "time, entryRoom, exitRoom, accel"

for key in sorted(dsData.keys()):
    print key, dsData[key].entryRoom, dsData[key].exitRoom, dsData[key].accel

print sorted(dsData.keys())
    
doorProcFile.close()
    
door1_data = lowPassFilter(door1_data_unfiltered)
door2_data = lowPassFilter(door2_data_unfiltered)

channelDiff(door1_data, door2_data, door_diff)

onePointDeriv1 = [0]
onePointDeriv2 = [0]

#do single point derivative
for i in range(1,len(door1_data)):
    onePointDeriv1.append(avgDeriv(door1_data[i-1:i+1], 0, 0)[0])
    
for i in range(1,len(door2_data)):
    onePointDeriv2.append(avgDeriv(door2_data[i-1:i+1], 0, 0)[0])

#door2_avg = average(door2_data[0:window_size*avgRange])
#door1_avg = average(door1_data[0:window_size*avgRange])

calcDoorDeriv(door1_data, door2_data, tdoor_data, door1_deriv, door2_deriv, door_diff, diff_deriv, window_size, avgRange)

# if the file = None, the raw data file was empty


#accelProcFile = open("Data_Deployment_1/Relay_Station_9999/Accelerometer/Accelerometer2015-08-31_8-44", "r")
#taccel_data, x_data, y_data, z_data = plotAccel(accelProcFile)

#lightProcFile = open("Data_Deployment_1/Relay_Station_9999/Light/Ambient Light2015-08-31_8-40", "r")
#tlight_data, light_data = plotLight(lightProcFile)

#tempProcFile = open("Data_Deployment_1/Relay_Station_9999/Temperature/Temperature2015-08-31_8-40", "r")
#tTemp_data, temp_data = plotTemp(tempProcFile)

#soundProcFile = open("Data_Deployment_1/Relay_Station_9999/Audio/Ambient Noise2015-08-31_8-40", "r")
#tsound_data, sound_data = plotNoise(soundProcFile)

        

app = QtGui.QApplication([])
           
win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('BESI Data from Last Saved Session')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Accel Plot
p1 = win.addPlot(title="Accelerometer Data")
p1.setLabel('left', "Uncalibrated Accelerometer", units='')
p1.setLabel('bottom', "Time", units='s')
p1.plot(tdoor_data ,door1_data, pen=(255,0,0), name="Filtered")
p1.plot(tdoor_data ,door2_data, pen=(0,255,0), name="Filtered")
p1.plot(tdoor_data ,door1_deriv, pen=(0,0,255), name="Filtered")
p1.plot(tdoor_data ,door2_deriv, pen=(0,255,255), name="Filtered")



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
