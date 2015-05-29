# produces a time series of light level data from a processed file

def plotLight(inFile):

    time_data = []
    light_data = []
    
    # first line is the start date and time
    inFile.readline()
    
    # ignore line with metadata 
    inFile.readline()
    
    for line in inFile:
        splitData = line.split(",")
        #print splitData
        try:
            time_data.append(float(splitData[0]))
            light_data.append(float(splitData[1]))
        except:
            print "error processing float"
            
    return time_data, light_data