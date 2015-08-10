# BESI project basestation program
# plots data for a single relay station from processes data files

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from processAccel import plotAccel, calibrateMagnitude
from processLight import plotLight
from processNoise import plotNoise
from processTemp import plotTemp, lowPassFilter
import numpy

# returns an array of moving averages using an avgLen point average
def moving_avg(data, avgLen):
    moving_avg = []
    if len(data) > 0:
        for i in range(len(data) + 1):
            if i < avgLen and i > 0:
                moving_avg.append(sum(data[:i])/i)
            elif i >= avgLen:
                moving_avg.append(float(sum(data[i - avgLen:i])/avgLen))
    return moving_avg

downsampleRate = 1

#fname1 = "data/Accelerometer2015-06-09_V2"
fname2 = "data/Ambient Light2015-06-09_10-28"
#fname3 = "data/Ambient Noise2015-06-09_10-28"
fname4 = "data/Temperature2015-06-09_10-28"

"""
# plot<sensor> functions take the processed file and return arrays to plot
if fname1 != None:
    accelProcFile = open(fname1, "r")
    #accelProcFile = open("data/Accelerometer2015-07-06_15-18", "r")
    t_data, x_data, y_data, z_data = plotAccel(accelProcFile)
"""
# if the file = None, the raw data file was empty
if fname2 != None:
    lightProcFile = open(fname2, "r")
    #lightProcFile = open("data/Ambient Light2015-06-03", "r")
    tlight_data, light_data = plotLight(lightProcFile)
else:
    lightProcFile = None
    tlight_data = []
    light_data = []
"""    
if fname3 != None:
    noiseProcFile = open(fname3, "r")
    #noiseProcFile = open("data/Ambient Noise2015-06-03", "r")
    tnoise_data, noise_data = plotNoise(noiseProcFile)
else:
    noiseProcFile = None
    tnoise_data = []
    noise_data = []
    
"""
    
if fname4 != None:
    tempProcFile = open(fname4, "r")
    #tempProcFile = open("data/Temperature2015-06-03", "r")
    tTemp_data, temp_data = plotTemp(tempProcFile)
else:
    tempProcFile = None
    temp_data = []
    tTemp_data = []
        

# This can be uncommented to plot processed data from a previous session





app = QtGui.QApplication([])
           
win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('BESI Data from Last Saved Session')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Accel Plot
#p1 = win.addPlot(title="Accelerometer Data")
#p1.setLabel('left', "Uncalibrated Accelerometer", units='')
#p1.setLabel('bottom', "Time", units='s')
#p1.plot(t_data, calibrateMagnitude(t, x_data, y_data, z_data), pen=(255,0,0), name="Accel curve")
#p1.plot(t_data[0::downsampleRate], x_data[0::downsampleRate], pen=(0,255,0), name="X curve") # green
#p1.plot(t_data[0::downsampleRate], y_data[0::downsampleRate], pen=(0,0,255), name="Y curve") # Blue
#p1.plot(t_data, lowPassFilter(x_data), pen=(0,255,0), name="X curve") # green
#p1.plot(t_data, lowPassFilter(y_data), pen=(0,0,255), name="Y curve") # Blue
#p1.plot(t_data[0::downsampleRate], z_data[0::downsampleRate], pen=(255,0,255), name="Z curve") # purple


# Light Plot
p2 = win.addPlot(title="Ambient Light Data")
p2.setLabel('left', "Light Level", units='Lux')
p2.setLabel('bottom', "Time", units='s')
p2.plot(tlight_data, light_data, pen=(0,255,0), name="Filtered")

#win.nextRow()

# Plot Noise
#p3 = win.addPlot(title="Ambient Noise Data")
#p3.setLabel('left', "Noise Amplitude over 0.1s of data", units='V')
#p3.setLabel('bottom', "Time", units='s')
#p3.plot(tnoise_data, noise_data, pen=(0,255,0), name="Filtered")

# plot temperature
p4 = win.addPlot(title="Temperature Data")
p4.setLabel('left', "Temperature (raw and LPF)", units='Degree F')
p4.setLabel('bottom', "Time", units='s')
p4.plot(tTemp_data, temp_data, pen=(0,255,0), name="Filtered")

temp_lpf = lowPassFilter(temp_data)

temp_std = numpy.std(temp_data)
temp_avg = moving_avg(temp_data, 500)

temp_plusSTD = []
for i in range(len(temp_avg)):
    temp_plusSTD.append(temp_avg[i] + 2 * temp_std)
    
temp_minusSTD = []
for i in range(len(temp_avg)):
    temp_minusSTD.append(temp_avg[i] - 2 * temp_std)
p4.plot(tTemp_data, temp_lpf, pen=(0,100,255), name="Unfiltered")
p4.plot(tTemp_data, temp_avg, pen=(0,0,255), name="Unfiltered")   
p4.plot(tTemp_data, temp_plusSTD, pen='r', name="Unfiltered")
p4.plot(tTemp_data, temp_minusSTD, pen='r', name="Unfiltered")

light_std = numpy.std(light_data)
light_avg = moving_avg(light_data, 100)

light_plusSTD = []
for i in range(len(light_avg)):
    light_plusSTD.append(light_avg[i] + 2 * light_std)
    
light_minusSTD = []
for i in range(len(light_avg)):
    light_minusSTD.append(light_avg[i] - 2 * light_std)
    
temp_data2 = []
for i in range(len(temp_avg)):
    if temp_data[i] > temp_plusSTD[i] or temp_data[i] < temp_minusSTD[i]:
        temp_data2.append(temp_avg[i])
    else:
        temp_data2.append(temp_data[i])
        
temp_avg2 = moving_avg(temp_data2, 500)
    
correl = []
for i in range(12500):
    correl.append(numpy.corrcoef(light_avg[i:5000 + i], temp_avg[i:5000 + i])[1][0])


# derivative of temperature
temp_deriv = []
for i in range(len(temp_avg2) - 600):
    temp_deriv.append(temp_avg2[i + 600]- temp_avg2[i])

# integral of light level
light_offset = numpy.mean(light_data)
light_int = []
for i in range(len(light_data)):
    if i == 0:
        light_int.append(light_data[i] - light_offset)
    else:
        light_int.append(light_int[i-1] + light_data[i] - light_offset)
 
p2.plot(tlight_data, light_avg, pen=(0,0,255), name="Unfiltered")   
p2.plot(tlight_data, light_plusSTD, pen='r', name="Unfiltered")
p2.plot(tlight_data, light_minusSTD, pen='r', name="Unfiltered")
print numpy.corrcoef(light_avg[0:17000], temp_avg[0:17000])

win.nextRow()

#p3 = win.addPlot(title="Ambient Noise Data")
#p3.setLabel('left', "Noise Amplitude over 0.1s of data", units='V')
#p3.setLabel('bottom', "Time", units='s')
#p3.plot(tlight_data, light_int, pen=(0,0,255), name="Unfiltered") 
#p3.plot(light_data[:17500], temp_data[:17500], pen=None, symbol='t', symbolPen=None, symbolSize=1, symbolBrush=(100, 100, 255, 50))


p1 = win.addPlot(title="Ambient Noise Data")
p1.setLabel('left', "Noise Amplitude over 0.1s of data", units='V')
p1.setLabel('bottom', "Time", units='s')
p1.plot(tTemp_data[:len(temp_deriv)], temp_deriv, pen=(0,0,255), name="Unfiltered")
#p1.plot(tTemp_data[:len(correl)], correl, pen=(0,0,255), name="Unfiltered")


#accelProcFile.close()
#if lightProcFile !=None:
#    lightProcFile.close()
    
#if noiseProcFile != None:
#    noiseProcFile.close()
    
p3 = win.addPlot(title="Ambient Light Data")
p3.setLabel('left', "Light Level", units='Lux')
p3.setLabel('bottom', "Time", units='s')
p3.plot(tTemp_data, temp_data2, pen=(0,255,0), name="Filtered")
p3.plot(tTemp_data, temp_avg2, pen=(0,0,255), name="Unfiltered")   
p3.plot(tTemp_data, temp_plusSTD, pen='r', name="Unfiltered")
p3.plot(tTemp_data, temp_minusSTD, pen='r', name="Unfiltered")
    
    
if tempProcFile != None:
    tempProcFile.close()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()