# produces a time series of noise level data from a processed file
# Noise is passed through a high pass filter on the BBB

def plotNoise(inFile):
    time_data = []
    noise_data = []
    
    # read starting time and date
    inFile.readline()
    
    # ignore line with metadata 
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