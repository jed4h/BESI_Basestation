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

def rssi_filter(rssi_data):
    sampleNum = 5000
    avg = []
    for i in range(sampleNum):
        avg.append(-200)
    
    total = 0
    for i in range(len(rssi_data)):
        if i < sampleNum:
            total = total + rssi_data[i]
        else:
            avg.append(total/sampleNum)
            total = total + rssi_data[i] - rssi_data[i-sampleNum]
     
    return avg        
           
#find the index 
def time_to_index(t_data, time):
    value = min(t_data, key=lambda x:abs(x-time))       
    return t_data.index(value)

def rssi_change(t_data, time, rssi_data):
    time_range = 10
    event_index = time_to_index(t_data, time)
    
    if (time -1*time_range > 0):
        start_index = time_to_index(t_data, time - time_range)
    else:
        start_index = 0
        
    end_index = time_to_index(t_data, time + time_range)
    
    if len(rssi_data[start_index:event_index]) != 0:
        start_rssi = sum(rssi_data[start_index:event_index])/len(rssi_data[start_index:event_index])
    else:
        start_rssi = -200
        
    if len(rssi_data[event_index:end_index]) != 0:
        end_rssi = sum(rssi_data[event_index:end_index])/len(rssi_data[event_index:end_index])
    else:
        end_rssi = -200
       
    print time,start_rssi,end_rssi
      

root = tk.Tk()
root.withdraw()

downsampleRate = 1

print "Select an accelerometer file to plot"
fname1 = tkFileDialog.askopenfilename()
print "Select a light level file to plot"
#fname2 = tkFileDialog.askopenfilename()
print "Select an ambient noise file to plot"
#fname3 = tkFileDialog.askopenfilename()
print "Select a temperature file to plot"
#fname4 = tkFileDialog.askopenfilename()

fname2 = None
fname3 = None
fname4 = None

# plot<sensor> functions take the processed file and return arrays to plot
if fname1 != None:
    accelProcFile = open(fname1, "r")
    #accelProcFile = open("data/Accelerometer2015-07-06_15-18", "r")
    t_data, x_data, y_data, z_data, rssi_data = plotAccel(accelProcFile)

# if the file = None, the raw data file was empty
if fname2 != None:
    lightProcFile = open(fname2, "r")
    #lightProcFile = open("data/Ambient Light2015-06-03", "r")
    tlight_data, light_data = plotLight(lightProcFile)
else:
    lightProcFile = None
    tlight_data = []
    light_data = []
    
if fname3 != None:
    noiseProcFile = open(fname3, "r")
    #noiseProcFile = open("data/Ambient Noise2015-06-03", "r")
    tnoise_data, noise_data = plotNoise(noiseProcFile)
else:
    noiseProcFile = None
    tnoise_data = []
    noise_data = []
    
if fname4 != None:
    tempProcFile = open(fname4, "r")
    #tempProcFile = open("data/Temperature2015-06-03", "r")
    tTemp_data, temp_data = plotTemp(tempProcFile)
else:
    tempProcFile = None
    temp_data = []
    tTemp_data = []
        

app = QtGui.QApplication([])
           
win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('BESI Data from Last Saved Session')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# 

for i in range(len(t_data)):
    t_data[i] = t_data[i] + 0

# entry/exit events

entries = []
exits = []

offset = 0

entry_times = [47, 81, 143,188, 207, 216, 228, 233, 257, 299, 307, 308, 314, 337, 342, 362]

#entry_times = [95, 46, 51, 182, 209, 227, 245, 335, 346, 381, 389, 135, 148, 192, 204, 268, 273, 291, 309, 330, 357, 232, 241, 343, 365, 139, 191, 223, 251, 317, 327]
exit_times = []

for tstamp in t_data:
    if entry_times.count(round(tstamp + offset)):
        entries.append(0)
    else:
        entries.append(-200)
        
    if exit_times.count(round(tstamp + offset)):
        exits.append(0)
    else:
        exits.append(-200)
        
for i in range(len(rssi_data)):
    if rssi_data[i] == 0 and x_data[i] == 0:
        rssi_data[i] = -200
        
    if rssi_data[i] < -200:
        rssi_data[i] = -200

for event in entry_times:
    rssi_change(t_data, event-offset, rssi_data)
    
for event in exit_times:
    rssi_change(t_data, event-offset, rssi_data)

# Accel Plot
p1 = win.addPlot(title="Accelerometer Data")
p1.setLabel('left', "Uncalibrated Accelerometer", units='')
p1.setLabel('bottom', "Time", units='s')
#p1.plot(t_data, calibrateMagnitude(t, x_data, y_data, z_data), pen=(255,0,0), name="Accel curve")
p1.plot(t_data[0::downsampleRate], x_data[0::downsampleRate], pen=(0,255,0), name="X curve") # green
p1.plot(t_data[0::downsampleRate], y_data[0::downsampleRate], pen=(0,0,255), name="Y curve") # Blue
#p1.plot(t_data, lowPassFilter(x_data), pen=(0,255,0), name="X curve") # green
#p1.plot(t_data, lowPassFilter(y_data), pen=(0,0,255), name="Y curve") # Blue
p1.plot(t_data[0::downsampleRate], z_data[0::downsampleRate], pen=(255,0,255), name="Z curve") # purple
p1.plot(t_data[0::downsampleRate], rssi_data[0::downsampleRate], pen=(255,255,255), name="RSSI curve") # purple
#p1.plot(t_data[0::downsampleRate], entries[0::downsampleRate], pen=(0,0,255), name="RSSI curve") # blue
#p1.plot(t_data[0::downsampleRate], exits[0::downsampleRate], pen=(255,0,0), name="RSSI curve") # red

"""
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
p4.plot(tTemp_data, lowPassFilter(lowPassFilter(temp_data)), pen=(0,255,0), name="Filtered")
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
"""

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        
        
