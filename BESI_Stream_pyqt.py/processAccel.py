# functions to process raw Shimmer3 accelerometer data and produce arrays of timestamps and data to plot
import datetime
import math
from parameters import *

# computes the calibrated accelerometer magnitude from raw measurements for each axis
def calibrateMagnitude(t, x, y, z, calibSession):
    
    # these variables are used to account for corrupted packets
    last_valid = False
    t_last = 0
    invalid_count = 0
    
    x_calib = []
    y_calib = []
    z_calib = []
    accelMag = []
    
    remove_corrupted = True
    
    # a reading of 0 indicates no connection
    # if remove_corrupted is True, invalid entries (due to lost or currupted packets) are replaced with 0s
    for i in range(len(x)):
        # check if the last timestamp is valid and if the current is the last plus 320 (or + 640 if the shimmer misses a sample)
        if (not remove_corrupted or (not last_valid) or (int(t[i]) == int(t_last) + TICKS_PER_SAMPLE) or (int(t[i]) == int(t_last) + 2 * TICKS_PER_SAMPLE) or (int(t[i]) == int(t_last) + TICKS_PER_SAMPLE - SHIMMER_TICKS) or (int(t[i]) == int(t_last) + 2 * TICKS_PER_SAMPLE - SHIMMER_TICKS)):
            last_valid = True
            #t_last = t[i]
            if (x[i] != 0):
                x_calib.append((x[i] - calibSession.xOff)/calibSession.xSens)
            else:
                x_calib.append(0)
                
            if (y[i] != 0):
                y_calib.append((y[i] - calibSession.yOff)/calibSession.ySens)
            else:
                y_calib.append(0)
                
            if (z[i] != 0):
                z_calib.append((z[i] - calibSession.zOff)/calibSession.zSens)
            else:
                z_calib.append(0)
                
            accelMag.append(math.sqrt(x_calib[-1]**2 + y_calib[-1]**2 + z_calib[-1]**2))
            
        else:
            # corrupted packet - ignore 16 readings and write 0s instead
            # TODO: use more intelligent method to check the number of corrupted samples
            accelMag.append(0)
            invalid_count = invalid_count + 1
            print t_last
            print t[i]
            if invalid_count == CORRUPTED_COUNT:
                invalid_count = 0
                last_valid = False
        
    return accelMag
  
# processes timestamps from a file of raw accel. data
# the raw timestamp is the number of ticks of a 32768 Hz clock that resets to 0 every 2 seconds (16 bit counter)
# the processed timestamp is the time since the last Bluetooth connection event  
# the raw timestamps from Shimmer are returned to use to check for corrupted packets
##############
##Deprecated##
##############
def processTimestampAccel(accelFile, port, DeploymentID):
    t = []
    lastTime = 0
    # initial value needs to be > -640 so the first sample does not look like it is 2 samples after this
    lastRelTime = -10000
    startDate =  accelFile.readline()
    
    try:
        dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Accelerometer File"
        return None
   
    # file name is based on start date and time of session
    fname = "data/Accelerometer{0}_{1}-{2:02}".format(dt.date(), dt.time().hour, dt.time().minute)
    outputFile = open(fname, "w")
    
    outputFile.write(startDate)
    outputFile.write("Timestamp,X-Axis,Y-Axis,Z-Axis\n")
    outputFile.write("Deployment ID: {0}, Relay Station ID: {1}\n".format(DeploymentID, port))
    
    for line in accelFile:
        data = line.split(",")
        try:
            relTime, xAxis, yAxis, zAxis, nLine = data
        except: # line is a datetime object or an incomplete line
            try:
                datetime.datetime.strptime(line.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
            except:
                pass
            else:
                # write datetime timestamp
                outputFile.write(data[0])
                #print "found a date"
                # time is reset for each disconnect event
                lastTime = 0 
        else:
            # for each valid data entry, the time stamp is incremented by the time between samples
            # check for a single missed sample
            if (int(relTime) == lastRelTime + 2 * TICKS_PER_SAMPLE) or (int(relTime) == lastRelTime + 2 * TICKS_PER_SAMPLE - SHIMMER_TICKS):
                lastTime = lastTime + 2 * TICK_TIME
            else:
                lastTime = lastTime + TICK_TIME
            t.append(relTime)
            lastRelTime = int(relTime)
            outputFile.write("{0:.2f},{1},{2},{3}\n".format(float(lastTime), xAxis, yAxis, zAxis))
            
    return fname, t
  
# reads a file of accelerometer data and returns arrays to be plotted
##############
##Deprecated##
##############
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
    
    try:
        dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Accelerometer File"
        return None
    
    outputFile = open("data/Accelerometer{}_V2".format(dt.date()), "w")
    outputFile.write(startDate)
    
    # convert into seconds
    startTime = dt.time().hour * 3600 + dt.time().minute * 60 + dt.time().second + dt.time().microsecond /1000000.0
    # timeOffset is used to correct for periods when the connection is lost
    timeOffset = 0
    
    # ignore line with metadata 
    outputFile.write(inFile.readline())
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


# processes timestamps from shimmer, writes the results to a file and returns arrays to plot
def processAccel(accelFile, port, DeploymentID):
    t = []
    lastTime = 0
    
    t_data = []
    x_data = []
    y_data = []
    z_data = []
    
    # initial value needs to be > -640 so the first sample does not look like it is 2 samples after this
    lastRelTime = -10000
    startDate =  accelFile.readline()
    
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Accelerometer File"
        return None, [], [], [], [], []
   
    # file name is based on start date and time of session
    fname = "data/Accelerometer{0}_{1}-{2:02}".format(dt.date(), dt.time().hour, dt.time().minute)
    outputFile = open(fname, "w")
    
    outputFile.write(startDate)
    outputFile.write("Timestamp,X-Axis,Y-Axis,Z-Axis\n")
    outputFile.write("Deployment ID: {0}, Relay Station ID: {1}\n".format(DeploymentID, port))
    
    # convert into seconds
    startTime = dt.time().hour * 3600 + dt.time().minute * 60 + dt.time().second + dt.time().microsecond /1000000.0
    # timeOffset is used to correct for periods when the connection is lost
    timeOffset = 0
    
    for line in accelFile:
        data = line.split(",")
        try:
            relTime, xAxis, yAxis, zAxis, nLine = data
        except: # line is a datetime object or an incomplete line
            try:
                datetime.datetime.strptime(line.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
            except:
                pass
            else:
                # write datetime timestamp
                #outputFile.write(data[0])
                #print "found a date"
                # time is reset for each disconnect event
                t = dt.time().hour * 3600 + dt.time().minute * 60 + dt.time().second + dt.time().microsecond /1000000.0
                timeOffset = t - startTime
                lastTime = 0
        else:
            # for each valid data entry, the time stamp is incremented by the time between samples
            # check for a single missed sample
            if (int(relTime) == lastRelTime + 2 * TICKS_PER_SAMPLE) or (int(relTime) == lastRelTime + 2 * TICKS_PER_SAMPLE - SHIMMER_TICKS):
                lastTime = lastTime + 2 * TICK_TIME
            else:
                lastTime = lastTime + TICK_TIME
            # t is the raw timestamps from shimmer
            t.append(relTime)
            lastRelTime = int(relTime)
            t_data.append(float(lastTime) + timeOffset)
            x_data.append(int(xAxis))
            y_data.append(int(yAxis))
            z_data.append(int(zAxis))
            outputFile.write("{0:.2f},{1},{2},{3}\n".format(float(lastTime), int(xAxis), int(yAxis), int(zAxis)))
            
    return fname, t, t_data, x_data, y_data, z_data