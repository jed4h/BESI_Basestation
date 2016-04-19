# BESI project basestation program
# plots data for a single relay station from processes data files

#TODO: should plot all data from a given deployment

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from processAccel import plotAccel
from processLight import plotLightTimeStamp
from processNoise import plotNoiseStartTime
from processTemp import plotTempStartTime, lowPassFilter
from processDoor import plotDoorStartTime
import Tkinter as tk
import tkFileDialog
from os import listdir

def concatLight(deployID, relayID, light_data, t_data):
    basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayID) + "/"
    lastStartTime = 0
    totalOffset = 0
    offset = 0
    
    for fileName in  listdir(basePath + "Light"):
        lightProcFile = open(basePath + "Light/" + fileName, "r")
        tlight_data_tmp, light_data_tmp, startTime = plotLightTimeStamp(lightProcFile)
        
        if lastStartTime != 0:
            offset = startTime - lastStartTime
            offset = offset.days * 86400 + offset.seconds + offset.microseconds/100000.0
                
        if tlight_data_tmp[0] == 0:
            totalOffset = totalOffset + offset
            lastStartTime = startTime
        
        for tValue in tlight_data_tmp:
            t_data.append((tValue + totalOffset)/3600)
        
        for lightValue in light_data_tmp:
            light_data.append(lightValue)
            
        lightProcFile.close()
        
def concatSound(deployID, relayID, sound_data, t_data):
    basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayID) + "/"
    lastStartTime = 0
    totalOffset = 0
    offset = 0
    
    for fileName in  listdir(basePath + "Audio"):
        soundProcFile = open(basePath + "Audio/" + fileName, "r")
        tsound_data_tmp, sound_data_tmp, startTime = plotNoiseStartTime(soundProcFile)
        
        if lastStartTime != 0:
            offset = startTime - lastStartTime
            offset = offset.days * 86400 + offset.seconds + offset.microseconds/100000.0
               
        if tsound_data_tmp[0] == 0:
            totalOffset = totalOffset + offset
            lastStartTime = startTime
        
        # average sound every second
        for i in range(len(tsound_data_tmp)/500):
            t_data.append((tsound_data_tmp[i*500] + totalOffset)/3600)
            sound_data.append(sum(sound_data_tmp[i:i+499])/500)
        
        soundProcFile.close()
        
def concatTemp(deployID, relayID, temp_data, t_data):
    basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayID) + "/"
    lastStartTime = 0
    totalOffset = 0
    offset = 0
    
    for fileName in  listdir(basePath + "Temperature"):
        tempProcFile = open(basePath + "Temperature/" + fileName, "r")
        tTemp_data_tmp, temp_data_tmp, startTime = plotTempStartTime(tempProcFile)
        
        if lastStartTime != 0:
            offset = startTime - lastStartTime
            offset = offset.days * 86400 + offset.seconds + offset.microseconds/100000.0
                
        if tTemp_data_tmp[0] < 5:
            totalOffset = totalOffset + offset
            lastStartTime = startTime
        
        for tValue in tTemp_data_tmp:
            t_data.append((tValue + totalOffset)/3600)
        
        for tempValue in temp_data_tmp:
            temp_data.append(tempValue)
            
        tempProcFile.close()
        
def concatDoor(deployID, relayID, door_data1, door_data2, t_data):
    basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayID) + "/"
    lastStartTime = 0
    totalOffset = 0
    offset = 0
    
    for fileName in  listdir(basePath + "Door"):
        doorProcFile = open(basePath + "Door/" + fileName, "r")
        tdoor_data_tmp, door_data_tmp1, door_data_tmp2, startTime = plotDoorStartTime(doorProcFile)
        
        if lastStartTime != 0:
            offset = startTime - lastStartTime
            offset = offset.days * 86400 + offset.seconds + offset.microseconds/100000.0
               
        if tdoor_data_tmp[0] < 5:
            totalOffset = totalOffset + offset
            lastStartTime = startTime
        
        # average sound every second
        for i in range(len(tdoor_data_tmp)/5):
            t_data.append((tdoor_data_tmp[i*5] + totalOffset)/3600)
            door_data1.append(sum(door_data_tmp1[i:i+4])/5)
            door_data2.append(sum(door_data_tmp2[i:i+4])/5)
        
        doorProcFile.close()

taccel_data = []
x_data = []
y_data = []
z_data = []

tlight_data1 = []
light_data1 = []
tlight_data2 = []
light_data2 = []
tlight_data3 = []
light_data3 = []
tlight_data4 = []
light_data4 = []
tlight_data5 = []
light_data5 = []
tlight_data6 = []
light_data6 = []

tTemp_data1 = []
temp_data1 = []
tTemp_data2 = []
temp_data2 = []
tTemp_data3 = []
temp_data3 = []
tTemp_data4 = []
temp_data4 = []
tTemp_data5 = []
temp_data5 = []
tTemp_data6 = []
temp_data6 = []

tSound_data1 = []
sound_data1 = []
tSound_data2 = []
sound_data2 = []
tSound_data3 = []
sound_data3 = []
tSound_data4 = []
sound_data4 = []
tSound_data5 = []
sound_data5 = []
tSound_data6 = []
sound_data6 = []

tsound_data = []
sound_data = []
tTemp_data = []
temp_data = []

tdoor_data1 = []
door_data11 = []
door_data12 = []
tdoor_data2 = []
door_data21 = []
door_data22 = []
tdoor_data3 = []
door_data31 = []
door_data32 = []
tdoor_data4 = []
door_data41 = []
door_data42 = []
tdoor_data5 = []
door_data51 = []
door_data52 = []

root = tk.Tk()
root.withdraw()

downsampleRate = 1

accelLastTime = 0

deployID = 50
relayID = 9999

basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayID) + "/"
"""
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
    
    try:
        accelLastTime = taccel_data[-1]
    except:
        accelLastTime = 0
        
    accelProcFile.close()
"""   

"""
concatLight(14, 9999, light_data1, tlight_data1)
concatLight(14, 10004, light_data2, tlight_data2)
concatLight(14, 10009, light_data3, tlight_data3)
concatLight(14, 10014, light_data4, tlight_data4)
concatLight(14, 10019, light_data5, tlight_data5)
concatLight(14, 10024, light_data6, tlight_data6)
"""
concatTemp(14, 9999, temp_data1, tTemp_data1)
concatTemp(14, 10004, temp_data2, tTemp_data2)
concatTemp(14, 10009, temp_data3, tTemp_data3)
concatTemp(14, 10014, temp_data4, tTemp_data4)
concatTemp(14, 10019, temp_data5, tTemp_data5)
concatTemp(14, 10024, temp_data6, tTemp_data6)

concatDoor(14, 9999, door_data11, door_data12, tdoor_data1)
concatDoor(14, 10004, door_data21, door_data22, tdoor_data2)
concatDoor(14, 10009, door_data31, door_data32, tdoor_data3)
concatDoor(14, 10014, door_data41, door_data42, tdoor_data4)
concatDoor(14, 10019, door_data51, door_data52, tdoor_data5)


"""
concatSound(14, 9999, sound_data1, tSound_data1)
concatSound(14, 10004, sound_data2, tSound_data2)
concatSound(14, 10009, sound_data3, tSound_data3)
concatSound(14, 10014, sound_data4, tSound_data4)
concatSound(14, 10019, sound_data5, tSound_data5)
concatSound(14, 10024, sound_data6, tSound_data6)
"""



"""
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
    
for fileName in  listdir(basePath + "Door"):
    doorProcFile = open(basePath + "Door/" + fileName, "r")
    tdoor_data_tmp, door1_data_tmp, door2_data_tmp = plotDoor(doorProcFile)
    
    for tValue in tdoor_data_tmp:
        tdoor_data.append(tValue)
    
    for doorValue in door1_data_tmp:
        door1_data.append(doorValue)
        
    for doorValue in door2_data_tmp:
        door2_data.append(doorValue)
        
    doorProcFile.close()
"""
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
    
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
    
        
win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('BESI Data from Last Saved Session')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

"""
# Accel Plot
p1 = win.addPlot(title="Accelerometer Data")
p1.setLabel('left', "Uncalibrated Accelerometer", units='')
p1.setLabel('bottom', "Time", units='s')
p1.plot(taccel_data ,x_data, pen=(255,0,0), name="Filtered")
p1.plot(taccel_data ,y_data, pen=(0,255,0), name="Filtered")
p1.plot(taccel_data ,z_data, pen=(0,0,255), name="Filtered")
"""

"""
# Temperature Plot
p2 = win.addPlot(title="Ambient Temperature")
p2.setLabel('left', "Temperature", units='F')
p2.setLabel('bottom', "Time", units='hours')
p2.plot(tTemp_data1, lowPassFilter(temp_data1), pen=(0,255,0), name="Filtered")
p2.plot(tTemp_data2, lowPassFilter(temp_data2), pen=(255,0,0), name="Filtered")
p2.plot(tTemp_data3, lowPassFilter(temp_data3), pen=(0,0,255), name="Filtered")
p2.plot(tTemp_data4, lowPassFilter(temp_data4), pen=(255,0,255), name="Filtered")
p2.plot(tTemp_data5, lowPassFilter(temp_data5), pen=(0,255,255), name="Filtered")
p2.plot(tTemp_data6, lowPassFilter(temp_data6), pen=(255,255,0), name="Filtered")
"""

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


"""
# Light Plot
p3 = win.addPlot(title="Ambient Light")
p3.setLabel('left', "Light Level", units='Lux')
p3.setLabel('bottom', "Time", units='hours')
p3.plot(tlightmin1, lowPassFilter(light_data1), pen=(0,255,0), name="Filtered")
p3.plot(tlightmin2, lowPassFilter(light_data2), pen=(255,0,0), name="Filtered")
p3.plot(tlightmin3, lowPassFilter(light_data3), pen=(0,0,255), name="Filtered")
p3.plot(tlightmin4, lowPassFilter(light_data4), pen=(255,0,255), name="Filtered")
p3.plot(tlightmin5, lowPassFilter(light_data5), pen=(0,255,255), name="Filtered")
p3.plot(tlightmin6, lowPassFilter(light_data6), pen=(255,255,0), name="Filtered")
"""


"""
# Plot Noise
p4 = win.addPlot(title="Ambient Sound")
p4.setLabel('left', "Sound Level", units='Envelope')
p4.setLabel('bottom', "Time", units='hours')
p4.plot(tSound_data1, sound_data1, pen=(0,255,0), name="Filtered")
p4.plot(tSound_data2, sound_data2, pen=(255,0,0), name="Filtered")
p4.plot(tSound_data3, sound_data3, pen=(0,0,255), name="Filtered")
p4.plot(tSound_data4, sound_data4, pen=(255,0,255), name="Filtered")
p4.plot(tSound_data5, sound_data5, pen=(0,255,255), name="Filtered")
p4.plot(tSound_data6, sound_data6, pen=(255,255,0), name="Filtered")
"""


p5 = win.addPlot(title="Door Sensor Data")
p5.setLabel('left', "Raw Door Sensor", units='')
p5.setLabel('bottom', "Time", units='hours')
p5.plot(tdoor_data1 ,door_data11, pen=(255,0,0), name="Filtered")
p5.plot(tdoor_data1 ,door_data12, pen=(0,255,0), name="Filtered")
"""
p5.plot(tdoor_data2 ,door_data21, pen=(255,0,0), name="Filtered")
p5.plot(tdoor_data2 ,door_data22, pen=(0,255,0), name="Filtered")
p5.plot(tdoor_data3 ,door_data31, pen=(255,0,0), name="Filtered")
p5.plot(tdoor_data3 ,door_data32, pen=(0,255,0), name="Filtered")
p5.plot(tdoor_data4 ,door_data41, pen=(255,0,0), name="Filtered")
p5.plot(tdoor_data4 ,door_data42, pen=(0,255,0), name="Filtered")
p5.plot(tdoor_data5 ,door_data51, pen=(255,0,0), name="Filtered")
p5.plot(tdoor_data5 ,door_data52, pen=(0,255,0), name="Filtered")
"""

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()