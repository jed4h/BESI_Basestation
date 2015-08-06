import datetime
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

# read raw accelerometer data from a file
#fileName = "data/Accelerometer2015-06-12_V2"

# low pass filter y[n] = .9y[n-1] + .1x[n]
def lowPassFilter(unfilteredData):
    filteredData = []
    if len(unfilteredData) > 2:
        filteredData.append(unfilteredData[0])
        
        for i in range(len(unfilteredData) - 1):
            filteredData.append(0.9 * filteredData[i] + 0.1 * unfilteredData[i + 1])
        
    else:
        filteredData = unfilteredData
    return filteredData
# 5 point moving average
def movingAvg(unfilteredData):
    filteredData = []
    if len(unfilteredData) > 5:
        for i in range(len(unfilteredData) - 4):
            filteredData.append(0.2 * unfilteredData[i] + 0.2 * unfilteredData[i+1] + 0.2 * unfilteredData[i+2] + 0.2 * unfilteredData[i+3] + 0.2 * unfilteredData[i+4])
        
    else:
        filteredData = unfilteredData
    return filteredData

def readData(fname):
    x = []
    y = []
    z = []
    time = []
    faccel = open(fname, "r")
    
    dateLine = faccel.readline()
    dt = datetime.datetime.strptime(dateLine.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    #startTime = dt.time().hour * 3600 + dt.time().minute * 60 + dt.time().second + dt.time().microsecond /1000000.0
    #print dt
    # discard line of metadata
    faccel.readline()
    
    for line in faccel:
        splitLine = line.split(",")
        #print splitLine
        # ignore lines with all 0s
        if (splitLine[1] == "0.0") and (splitLine[2] == "0.0") and (splitLine[3] == "0.0\n"):
            #print "found blank line"
            pass
        else:
            duration = splitLine[0]
            time.append(float(splitLine[0]))
            x.append(int(float(splitLine[1])))
            y.append(int(float(splitLine[2])))
            z.append(int(float(splitLine[3])))
            
    return time, x, y, z, duration

# peak detection based on thresholding
# negative peaks are clearer and larger than positive, so they are used
# a peak is found if the following occur:
# a point above the high threshold followed (not necessarily immediately) by a 
# point below the low threshold followed by a point above the high threshold
# an x peak followed by a y peak shows one pedal
def peakDetection(x, y, time):
    x_avg = 1285 # value when no motion is present
    x_offset = 250
    y_thresh_high = 2000
    y_thresh_low = 1500
    # a peak is detected when all three are 1
    x_peak0 = 0
    x_peak1 = 0
    x_peak2 = 0
    x_peak = 0
    intervals = []
    
    last_peak_time = 0
    
    
    y_peak0 = 0
    y_peak1 = 0
    y_peak2 = 0
    y_peak = 0
    
    pedal_count = 0
    
    for i in range(len(x)):
        x_sample = float(x[i])
        y_sample = float(y[i])
        
        """
        if y_sample > y_thresh_high:
            y_peak0 = 1
            
        if y_peak0 == 1 and y_sample < y_thresh_low:
            y_peak1 = 1
            
        if y_peak1 == 1 and y_sample > y_thresh_high:
            y_peak2 = 1
            
        if y_peak2 == 1:
            y_peak = 1
            y_peak0 = 0
            y_peak1 = 0
            y_peak2 = 0
            
        if x_peak == 1 and y_peak == 1:
            pedal_count = pedal_count + 1
            x_peak = 0
            y_peak = 0
            
        elif y_peak == 1 and x_peak == 0:
            y_peak = 0
        """   
        
        if x_sample > x_avg + x_offset:
            x_peak0 = 1
            
        if x_peak0 == 1 and x_sample < x_avg - x_offset:
            x_peak1 = 1
            
        if x_peak1 == 1 and x_sample > x_avg + x_offset:
            x_peak2 = 1
            
        if x_peak2 == 1:
            x_peak = 1
            x_peak0 = 0
            x_peak1 = 0
            x_peak2 = 0
            
        if x_peak == 1:
            pedal_count = pedal_count + 1
            intervals.append(60/(float(time[i]) - last_peak_time))
            last_peak_time = float(time[i])
            x_peak = 0
            
    return pedal_count, intervals

"""
time, x, y, z, duration = readData(fileName)
print duration
count, intervals = peakDetection(lowPassFilter(x), lowPassFilter(y), time)
print count



#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsWindow(title="Bike Cadence")
win.resize(1000,600)
win.setWindowTitle('Bike Cadence')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p1 = win.addPlot(title="Basic array plotting", y=movingAvg(intervals))
#p1 = win.addPlot(title="Rotations per Minute", y=intervals)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
"""           
