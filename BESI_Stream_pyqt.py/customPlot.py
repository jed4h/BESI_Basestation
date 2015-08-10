# BESI project basestation program
# plots data for a single relay station from processes data files

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from processAccel import plotAccel
from processLight import plotLight
from processNoise import plotNoise
from processTemp import plotTemp, lowPassFilter
import Tkinter as tk
import tkFileDialog

root = tk.Tk()
root.withdraw()

downsampleRate = 1


# if the file = None, the raw data file was empty


lightProcFile = open("data/Ambient Light2015-07-23_16-54", "r")
tlight_data, light_data = plotLight(lightProcFile)

lightProcFile2 = open("data/Ambient Light2015-07-23_16-54", "r")
tlight_data2, light_data2 = plotLight(lightProcFile2)

tempProcFile = open("data/Temperature2015-07-24_16-09", "r")
tTemp_data, temp_data = plotTemp(tempProcFile)

tempProcFile2 = open("data/Temperature2015-07-24_16-10", "r")
tTemp_data2, temp_data2 = plotTemp(tempProcFile2)

        

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
p1.plot(lowPassFilter(lowPassFilter(temp_data2)), pen=(0,255,0), name="Filtered")

# plot temperature
p2 = win.addPlot(title="Temperature Data")
p2.setLabel('left', "Temperature (raw and LPF)", units='Degree F')
p2.setLabel('bottom', "Time", units='s')
p2.plot(lowPassFilter(lowPassFilter(temp_data)), pen=(0,255,0), name="Filtered")
#p4.plot(tTemp_data, temp_data, pen=(0,0,255), name="Unfiltered")

win.nextRow()
tmpDelta = []
tmpDelta2 = []

filtered1 = temp_data[17:]
filtered2 = temp_data2

filtered3 = lowPassFilter(lowPassFilter(temp_data))
filtered4 = lowPassFilter(lowPassFilter(temp_data2))

for i in range(len(filtered1)):
    tmpDelta.append(filtered2[i] - filtered1[i])
    
for i in range(len(filtered3)):
    tmpDelta2.append(filtered4[i] - filtered3[i])

# Light Plot
p3 = win.addPlot(title="Ambient Light Data")
p3.setLabel('left', "Light Level", units='Lux')
p3.setLabel('bottom', "Time", units='s')
p3.plot(tmpDelta, pen=(0,255,0), name="Filtered")



# Plot Noise
p4 = win.addPlot(title="Ambient Noise Data")
p4.setLabel('left', "Noise Amplitude over 0.1s of data", units='V')
p4.setLabel('bottom', "Time", units='s')
p4.plot(tmpDelta2, pen=(255,0,0), name="Filtered")




## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()