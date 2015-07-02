# this file contains functions related to parsing the user input provided in the config file

def streamParseConfig():
    ports = []
    useAccel = []
    useLight = []
    useADC = []
    
    # Read config file
    fconfig = open("Configure.txt")
    
    for line in fconfig:
        #ignore comments
        if line[0] == "#":
            pass
        else:
            splitLine = line.split("=")
            try:
                if splitLine[0] == "xOff":
                    xOff = int(splitLine[1])
                    print "xOff: ",xOff
            except:
                print "Error processing x offset"
            
            try:
                if splitLine[0] == "yOff":
                    yOff = int(splitLine[1])
                    print "yOff: ",yOff
            except:
                print "Error processing y offset" 
            
            try:   
                if splitLine[0] == "zOff":
                    zOff = int(splitLine[1])
                    print "zOff: ",zOff
            except:
                print "Error processing z offset" 
            
            try:  
                if splitLine[0] == "xSens":
                    xSens = float(splitLine[1])
                    print "xSens: ",xSens
            except:
                print "Error processing x sensitivity" 
            
            try:    
                if splitLine[0] == "ySens":
                    ySens = float(splitLine[1])
                    print "ySens: ",ySens
            except:
                print "Error processing y sensitivity"
            
            try:   
                if splitLine[0] == "zSens":
                    zSens = float(splitLine[1])
                    print "zSens: ",zSens
            except:
                print "Error processing z sensitivity"
            
            try:
                if splitLine[0] == "ShimmerID":
                    ShimmerID = splitLine[1].rstrip()
                    print "ShimmerID: ",ShimmerID
            except:
                print "Error processing ShimmerID"
            
            try:
                if splitLine[0] == "PLOT":
                    PLOT = (splitLine[1] == "True\n")
                    print "plot: ",PLOT
            except:
                print "Error processing plot command"
            
            try:    
                if splitLine[0] == "numRelayStat":
                    numRelayStat = int(splitLine[1])
                    print "number of relay stations: ",numRelayStat
            except:
                print "Error processing the number of relay stations"
                
            try:
                if splitLine[0] == "DeploymentID":
                    DeploymentID = int(splitLine[1])
                    print "deployment ID: ",DeploymentID
            except:
                print "Error processing deployment ID"
             
            
            try:   
                if splitLine[0] == "PORT":
                    ports.append(int(splitLine[1]))
                    
                elif splitLine[0] == "USE_ACCEL":
                    useAccel.append(splitLine[1] == "True\n")
                    
                elif splitLine[0] == "USE_LIGHT":
                    useLight.append(splitLine[1] == "True\n")
                    
                elif splitLine[0] == "USE_ADC":
                    useADC.append(splitLine[1] == "True\n")
            except:
                "Error processing relay station parameters"
                
    return ports, useAccel, useLight, useADC, ShimmerID, PLOT, numRelayStat