# BESI project basestation program
# plots data for a single relay station from processes data files

#TODO: should plot all data from a given deployment

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

tdoor_data = []
door1_data = []
door2_data = []

root = tk.Tk()
root.withdraw()

downsampleRate = 1

accelLastTime = 0
startDatetime = "2016-03-06_01-32.txt"

deployID = input("Enter the Deployment ID number: ")
relayID = input("Enter the Relay Station ID number: ")

basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayID) + "/"

#for fileName in  listdir(basePath + "Door"):
doorProcFile = open(basePath + "Door/" + "Door Sensor" + startDatetime, "r")
tdoor_data_tmp, door1_data_tmp, door2_data_tmp = plotDoor(doorProcFile)

for tValue in tdoor_data_tmp:
    tdoor_data.append(tValue)

for doorValue in door1_data_tmp:
    door1_data.append(doorValue)
    
for doorValue in door2_data_tmp:
    door2_data.append(doorValue)
    
doorProcFile.close()
    


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



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()