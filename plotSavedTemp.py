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

# produces a time series of noise level data from a processed file
def plotTemp(inFile):

    time_data = []
    temp_data = []

    # first line is the start date and time
    inFile.readline()
    
    # ignore line with metadata 
    inFile.readline()
    
    for line in inFile:
        splitData = line.split(",")
        #print splitData
        try:
            time_data.append(float(splitData[0]))
            temp_data.append(float(splitData[2]))
        except:
            print "error processing float"

    return time_data, temp_data
