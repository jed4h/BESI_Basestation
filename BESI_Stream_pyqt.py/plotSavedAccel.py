# produces a time series of accelerometer data from a processed data file
# the timestamps are the time since the last reconnect event
# this program converts the timestamps into time relative to the start
import datetime
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import math

# computes the calibrated accelerometer magnitude from raw measurements for each axis
def calibrateMagnitude(x, y, z):
    # TODO: Think of a better way to store calib info
    # Assumes alignment is:    1 0 0
    #                          0 1 0
    #                          0 0 1
    xOff = 2086
    yOff = 2048
    zOff = 2050
    xSens = 84.0
    ySens = 83.0
    zSens = 83.0
    
    x_calib = []
    y_calib = []
    z_calib = []
    accelMag = []
    
    # a reading of 0 indicates no connection
    for i in range(len(x)):
        if (x[i] != 0):
            x_calib.append((x[i] - xOff)/xSens)
        else:
            x_calib.append(0)
            
        if (y[i] != 0):
            y_calib.append((y[i] - yOff)/ySens)
        else:
            y_calib.append(0)
            
        if (z[i] != 0):
            z_calib.append((z[i] - zOff)/zSens)
        else:
            z_calib.append(0)
            
        accelMag.append(math.sqrt(x_calib[-1]**2 + y_calib[-1]**2 + z_calib[-1]**2))
        
    return accelMag
    

def plotAccel(inFile):
    t_data = []
    x_data = []
    y_data = []
    z_data = []
    
    index = 0
    x = 0
    y = 0
    z = 0
    
    
    
   
    
    
    # after a disconnect the next line is a datetime string
    lineIsDate = False
    
    # first line holds the start date and time
    startDate =  inFile.readline()
    dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    
    outputFile = open("Accelerometer{}_V2".format(dt.date()), "w")
    outputFile.write(startDate)
    
    # convert into seconds
    startTime = dt.time().hour * 3600 + dt.time().minute * 60 + dt.time().second + dt.time().microsecond /1000000.0
    # timeOffset is used to correct for periods when the connection is lost
    timeOffset = 0
    
    # ignore line with metadata 
    outputFile.write(inFile.readline())
    
    for line in inFile:
        if lineIsDate:
            # if the line contains a date and time, adjust the timeOffset
            try:
                dt = datetime.datetime.strptime(line.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
            except:
                pass
            else:
                # convert into seconds
                t = dt.time().hour * 3600 + dt.time().minute * 60 + dt.time().second + dt.time().microsecond /1000000.0
                timeOffset = t - startTime
            lineIsDate = False
            
        # parse the line of data   
        else:
            for element in line.split(","):
                try:
                    float(element)
                except:
                    print "error processing float"
                else:
                    if index == 0:
                        # t is the time since the last bluetooth connection
                        t = float(element)
                        index = 1
                        
                        #if len(t) == 201:
                        #    t.pop(0)
                        #    x.pop(0)
                        #    y.pop(0)
                        #    z.pop(0)
                            
                    elif index == 1:
                        x = float(element)
                        index = 2
                    elif index == 2:
                        y = float(element)
                        index = 3
                    else:
                        z = float(element)
                        index = 0
            
            # connection is lost, next line is a time and date
            if x == 0 and y == 0 and z == 0:
                lineIsDate = True
                
            
            t_data.append(t + timeOffset)
            x_data.append(x)
            y_data.append(y)
            z_data.append(z)
            
    for i in range(len(t_data)):
        outputFile.write("{0},{1},{2},{3}\n".format(t_data[i], x_data[i], y_data[i], z_data[i]))
            
    return t_data, x_data, y_data, z_data