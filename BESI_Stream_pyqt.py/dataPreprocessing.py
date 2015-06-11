#  functions to process time stamps from data received from the BBB
import datetime
from parameters import *

# processes timestamps from a file of raw temp. data
# the raw timestamp is the time since the last sample
def processTemp(tempFile):
    lastTime = 0.0
    #first line is the start date/time of the data collection
    startDate =  tempFile.readline()
    dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    fname = "data/temperature{0}_{1}-{2:02}".format(dt.date(), dt.time().hour, dt.time().minute)
    outputFile = open(fname, "w")
    
    outputFile.write(startDate)
    outputFile.write("Timestamp,Degree C,Degree F\n")
    
    for line in tempFile:
        try:
            lastTime, tempDataC, tempDataF, nLine = line.split(",")
        except:
            # incomplete line - ignore
            pass
        else:
            # add timeDelta to the timestamp of the last sample to get the timestamp of the current sample
            #lastTime = lastTime + float(timeDelta)
            outputFile.write("{0},{1},{2}\n".format(float(lastTime), tempDataC, tempDataF))
            
    return fname

 
# raw sound data does not require any processing
# this function simply copies data and removes leading 0s 
def processSound(soundFile):
    startDate =  soundFile.readline()
    dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    fname = "data/Ambient Noise{0}_{1}-{2:02}".format(dt.date(), dt.time().hour, dt.time().minute)
    outputFile = open(fname, "w")
    
    outputFile.write(startDate)
    outputFile.write("Timestamp,Noise Level\n")
    
    for line in soundFile:
        try:
            lastTime, noiseLevel, nLine = line.split(",")
        except:
            # incomplete line - ignore
            pass
        else:
            outputFile.write("{0:.2f},{1:.2f}\n".format(float(lastTime), float(noiseLevel)))
        
    return fname


# raw light data does not require any processing
# this function simply copies data and removes leading 0s         
def processLight(lightFile):
    startDate =  lightFile.readline()
    dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    fname = "data/Ambient Light{0}_{1}-{2:02}".format(dt.date(), dt.time().hour, dt.time().minute)
    outputFile = open(fname, "w")
    
    outputFile.write(startDate)
    outputFile.write("Timestamp,Light Level\n")
    
    for line in lightFile:
        try:
            lastTime, lightLevel, nLine = line.split(",")
        except:
            # incomplete line - ignore
            pass
        else:
            outputFile.write("{0:.2f},{1:.2f}\n".format(float(lastTime), float(lightLevel)))
            
    return fname
       

# processes timestamps from a file of raw accel. data
# the raw timestamp is the number of ticks of a 32768 Hz clock that resets to 0 every second
# the processed timestamp is the time since the last Bluetooth connection event  
# the raw timestamps from Shimmer are returned to use to check for corrupted packets 
def processAccel(accelFile):
    t = []
    lastTime = 0
    lastRelTime = -10000
    startDate =  accelFile.readline()
    dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    fname = "data/Accelerometer{0}_{1}-{2:02}".format(dt.date(), dt.time().hour, dt.time().minute)
    outputFile = open(fname, "w")
    
    outputFile.write(startDate)
    outputFile.write("Timestamp,X-Axis,Y-Axis,Z-Axis\n")
    
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
