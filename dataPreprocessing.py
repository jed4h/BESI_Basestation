#  functions to process time stamps from data received from the BBB
import datetime

# processes timestamps from a file of raw temp. data
# the raw timestamp is the time since the last sample
def processTemp(tempFile):
    lastTime = 0.0
    #first line is the start date/time of the data collection
    startDate =  tempFile.readline()
    dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    outputFile = open("temperature{}".format(dt.date()), "w")
    
    outputFile.write(startDate)
    outputFile.write("Timestamp,Degree C,Degree F\n")
    
    for line in tempFile:
        timeDelta, tempDataC, tempDataF, nLine = line.split(",")
        # add timeDelta to the timestamp of the last sample to get the timestamp of the current sample
        lastTime = lastTime + float(timeDelta)
        outputFile.write("{0},{1},{2}\n".format(lastTime, tempDataC, tempDataF))
 
# raw sound data does not require any processing
# this function simply copies data and removes leading 0s 
def processSound(soundFile):
    startDate =  soundFile.readline()
    dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    outputFile = open("Ambient Noise{}".format(dt.date()), "w")
    
    outputFile.write(startDate)
    outputFile.write("Timestamp,Noise Level\n")
    
    for line in soundFile:
        try:
            lastTime, noiseLevel, nLine = line.split(",")
        except:
            pass
        else:
            outputFile.write("{0:.2f},{1:.2f}\n".format(float(lastTime), float(noiseLevel)))
        

# raw light data does not require any processing
# this function simply copies data and removes leading 0s         
def processLight(lightFile):
    startDate =  lightFile.readline()
    dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    outputFile = open("Ambient Light{}".format(dt.date()), "w")
    
    outputFile.write(startDate)
    outputFile.write("Timestamp,Light Level\n")
    
    for line in lightFile:
        lastTime, lightLevel, nLine = line.split(",")
        outputFile.write("{0:.2f},{1:.2f}\n".format(float(lastTime), float(lightLevel)))
       

# processes timestamps from a file of raw accel. data
# the raw timestamp is the number of ticks of a 32768 Hz clock that resets to 0 every second
# the processed timestamp is the time since the last Bluetooth connection event   
def processAccel(accelFile):
    lastTime = 0
    tick = 640.0/32768 # conversion between Shimmer assumes 51.2 Hz sampling rate
    startDate =  accelFile.readline()
    dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    outputFile = open("Accelerometer{}".format(dt.date()), "w")
    
    outputFile.write(startDate)
    outputFile.write("Timestamp,X-Axis,Y-Axis,Z-Axis\n")
    
    for line in accelFile:
        data = line.split(",")
        try:
            relTime, xAxis, yAxis, zAxis, nLine = data
        except: # line is a datetime object
            outputFile.write(data[0])
            # time is reset for each disconnect event
            lastTime = 0 
        else:
            # for each valid data entry, the time stamp is incremented by the between semples
            lastTime = lastTime + tick
            outputFile.write("{0:.2f},{1},{2},{3}\n".format(float(lastTime), xAxis, yAxis, zAxis))
