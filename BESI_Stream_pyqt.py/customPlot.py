# BESI project basestation program
# plots data for a single relay station from processes data files

#TODO: should plot all data from a given deployment

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from processAccel import plotAccel
from processLight import plotLight
from processNoise import plotNoise
from processTemp import plotTemp, lowPassFilter
import Tkinter as tk
import tkFileDialog
from os import listdir

taccel_data = []
x_data = []
y_data = []
z_data = []
tlight_data = []
light_data = []
tsound_data = []
sound_data = []
tTemp_data = []
temp_data = []

root = tk.Tk()
root.withdraw()

downsampleRate = 1

accelLastTime = 0

deployID = input("Enter the Deployment ID number: ")
relayID = input("Enter the Relay Station ID number: ")

basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayID) + "/"

for fileName in  listdir(basePath + "Accelerometer"):
    accelProcFile = open(basePath + "Accelerometer/" + fileName, "r")
    taccel_data_tmp, x_data_tmp, y_data_tmp, z_data_tmp = plotAccel(accelProcFile)
    
    for tValue in taccel_data_tmp:
        taccel_data.append(tValue + accelLastTime)
    
    for xValue in x_data_tmp:
        x_data.append(xValue)
        
    for yValue in y_data_tmp:
        y_data.append(yValue)
        
    for zValue in z_data_tmp:
        z_data.append(zValue)
    
    accelLastTime = taccel_data[-1]
    accelProcFile.close()
    
for fileName in  listdir(basePath + "Light"):
    lightProcFile = open(basePath + "Light/" + fileName, "r")
    tlight_data_tmp, light_data_tmp = plotLight(lightProcFile)
    
    for tValue in tlight_data_tmp:
        tlight_data.append(tValue)
    
    for lightValue in light_data_tmp:
        light_data.append(lightValue)
        
    lightProcFile.close()

for fileName in  listdir(basePath + "Audio"):
    soundProcFile = open(basePath + "Audio/" + fileName, "r")
    tsound_data_tmp, sound_data_tmp = plotNoise(soundProcFile)
    
    for tValue in tsound_data_tmp:
        tsound_data.append(tValue)
    
    for soundValue in sound_data_tmp:
        sound_data.append(soundValue)
        
    soundProcFile.close()
    
for fileName in  listdir(basePath + "Temperature"):
    tempProcFile = open(basePath + "Temperature/" + fileName, "r")
    tTemp_data_tmp, temp_data_tmp = plotTemp(tempProcFile)
    
    for tValue in tTemp_data_tmp:
        tTemp_data.append(tValue)
    
    for tempValue in temp_data_tmp:
        temp_data.append(tempValue)
        
    tempProcFile.close()

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
p1.plot(taccel_data ,x_data, pen=(255,0,0), name="Filtered")
p1.plot(taccel_data ,y_data, pen=(0,255,0), name="Filtered")
p1.plot(taccel_data ,z_data, pen=(0,0,255), name="Filtered")

# plot temperature
p2 = win.addPlot(title="Temperature Data")
p2.setLabel('left', "Temperature (raw and LPF)", units='Degree F')
p2.setLabel('bottom', "Time", units='s')
p2.plot(tTemp_data, lowPassFilter(lowPassFilter(temp_data)), pen=(0,255,0), name="Filtered")
#p4.plot(tTemp_data, temp_data, pen=(0,0,255), name="Unfiltered")

win.nextRow()
tmpDelta = []
tmpDelta2 = []

#filtered1 = temp_data[17:]
#filtered2 = temp_data2

#filtered3 = lowPassFilter(lowPassFilter(temp_data))
#filtered4 = lowPassFilter(lowPassFilter(temp_data2))

#for i in range(len(filtered1)):
#    tmpDelta.append(filtered2[i] - filtered1[i])
    
#for i in range(len(filtered3)):
#    tmpDelta2.append(filtered4[i] - filtered3[i])

# Light Plot
p3 = win.addPlot(title="Ambient Light Data")
p3.setLabel('left', "Light Level", units='Lux')
p3.setLabel('bottom', "Time", units='s')
p3.plot(tlight_data, light_data, pen=(0,255,0), name="Filtered")



# Plot Noise
p4 = win.addPlot(title="Ambient Noise Data")
p4.setLabel('left', "Noise Amplitude over 0.1s of data", units='V')
p4.setLabel('bottom', "Time", units='s')
p4.plot(tsound_data, sound_data, pen=(255,0,0), name="Filtered")




## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()