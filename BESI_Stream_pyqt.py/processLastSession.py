# Performs some processing on sensor data files,saves the files, and plots the data 
# File name is the sensor ID + the date it was recorded
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from processAccel import plotAccel, calibrateMagnitude
from processLight import plotLight
from processNoise import plotNoise
from processTemp import plotTemp, lowPassFilter
import os
from processParseConfig import processParseConfig
from processAccel import processAccel
from processLight import processLight
from processNoise import processSound
from processTemp import processTemp

#raw data files are named based on the socket port used to get the data from the BBB
basePort = int(raw_input("Enter the relay station ID: "))

# use a separate folder to save data files
if not os.path.exists("data"):
    os.mkdir("data")

# read config.txt to get the deployment ID
try:
    DeploymentID = processParseConfig()
except:
    print "Error reading configuration file"
    


try:
    rawAccelFile = open("data/accel" + "{}".format(basePort), "r")
    rawLightFile = open("data/light" + "{}".format(basePort + 1), "r")
    rawNoiseFile = open("data/sound" + "{}".format(basePort + 2), "r")
    rawTempFile = open("data/temp" + "{}".format(basePort + 3), "r")
except:
    print "Error opening raw data files"
    
else:
    # processing is mostly creating timestamps relative to he start of the data collection
    # these functions produce files name sensor ID + date
    # process accel does processing and returns arrays to plot. All the others just process and write to a file
    fname1, t, t_data, x_data, y_data, z_data = processAccel(rawAccelFile, basePort, DeploymentID)
    fname2 = processLight(rawLightFile, basePort, DeploymentID)
    fname3 = processSound(rawNoiseFile, basePort, DeploymentID)
    fname4 = processTemp(rawTempFile, basePort, DeploymentID)
    
    rawAccelFile.close()
    rawLightFile.close()
    rawNoiseFile.close()
    rawTempFile.close()
    
    # plot<sensor> functions take the processed file and return arrays to plot
    #if fname1 != None:
    #    accelProcFile = open(fname1, "r")
    
    # if the file = None, the raw data file was empty
    if fname2 != None:
        lightProcFile = open(fname2, "r")
        tlight_data, light_data = plotLight(lightProcFile)
    else:
        lightProcFile = None
        tlight_data = []
        light_data = []
        
    if fname3 != None:
        noiseProcFile = open(fname3, "r")
        tnoise_data, noise_data = plotNoise(noiseProcFile)
    else:
        noiseProcFile = None
        tnoise_data = []
        noise_data = []
        
    if fname4 != None:
        tempProcFile = open(fname4, "r")
        tTemp_data, temp_data = plotTemp(tempProcFile)
    else:
        tempProcFile = None
        temp_data = []
        tTemp_data = []
            
    """
    # This can be uncommented to plot processed data from a previous session
    accelProcFile = open("data/Accelerometer2015-06-12_11-13", "r")
    lightProcFile = open("data/Ambient Light2015-06-03", "r")
    noiseProcFile = open("data/Ambient Noise2015-06-03", "r")
    tempProcFile = open("data/Temperature2015-06-03", "r")
    """
    
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
    #p1.plot(t_data, calibrateMagnitude(t, x_data, y_data, z_data), pen=(255,0,0), name="Accel curve")
    p1.plot(t_data, x_data, pen=(0,255,0), name="X curve") # green
    p1.plot(t_data, y_data, pen=(0,0,255), name="Y curve") # Blue
    #p1.plot(t_data, lowPassFilter(x_data), pen=(0,255,0), name="X curve") # green
    #p1.plot(t_data, lowPassFilter(y_data), pen=(0,0,255), name="Y curve") # Blue
    p1.plot(t_data, z_data, pen=(255,0,255), name="Z curve") # purple
    
    
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
    
    # print the total time of recorded for each sensor
    try:
        print "Accel Duration: {}".format(t_data[-1])
    except:
        print "Accel Duration: 0"
        
    try:
        print "Light Duration: {}".format(tlight_data[-1])
    except:
        print "Light Duration: 0"
    
    try:
        print "Noise Duration: {}".format(tnoise_data[-1])
    except:
        print "Noise Duration: 0"
        
    try:
        print "Temp Duration: {}".format(tTemp_data[-1])
    except:
        print "Temp Duration: 0"
    
    #accelProcFile.close()
    if lightProcFile !=None:
        lightProcFile.close()
        
    if noiseProcFile != None:
        noiseProcFile.close()
        
    if tempProcFile != None:
        tempProcFile.close()
    
    
    ## Start Qt event loop unless running in interactive mode or using pyside.
    if __name__ == '__main__':
        import sys
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()