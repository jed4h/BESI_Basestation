from datetime import datetime

# raw sound data does not require any processing
# this function simply copies data and removes leading 0s 
def processSound(soundFile, port, DeploymentID):
    startDate =  soundFile.readline()
    
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        dt = datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Sound File"
        return None
    
    fname = "Data_Deployment_{0}/Relay_Station_{1}/Audio/Ambient Noise{2}_{3}-{4:02}".format(DeploymentID, port, dt.date(), dt.time().hour, dt.time().minute, DeploymentID)
    
    outputFile = open(fname, "w")
    
    outputFile.write(startDate)
    outputFile.write("Deployment ID: {0}, Relay Station ID: {1}\n".format(DeploymentID, port))
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

# produces a time series of noise level data from a processed file
# Noise is passed through a high pass filter on the BBB

def plotNoise(inFile):
    time_data = []
    noise_data = []
    
    # read starting time and date
    inFile.readline()
    
    # ignore lines with metadata 
    inFile.readline()
    inFile.readline()
    
    for line in inFile:
        splitData = line.split(",")
        #print splitData
        try:
            time_data.append(float(splitData[0]))
            noise_data.append(float(splitData[1]))
        except:
            print "error processing float"

        
    return time_data, noise_data