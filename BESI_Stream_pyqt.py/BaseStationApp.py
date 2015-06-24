import stream
import multiprocessing
from parameters import *
import os
import socket

if __name__ == '__main__':
    
    ports = []
    useAccel = []
    useLight = []
    useADC = []
    streamingProcs = []
    
    # use a separate folder to save data files
    if not os.path.exists("data"):
        os.mkdir("data")
        
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
                if splitLine[0] == "SAMPLING_RATE":
                    SAMPLING_RATE = float(splitLine[1])
                    print "Sampling Rate: ",SAMPLING_RATE
            except:
                print "Error processing Sampling Rate"
            
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
                
    print "Relay Station IDs: ",ports
    print "Use Accelerometer: ",useAccel
    print "Use Microphone and Temperature Sensor: ",useADC
    print "Use Light Sensor", useLight
        
    name = socket.gethostname()   
    try:
        host = socket.gethostbyname(name)
        print "Basestation IP Address: ",host
    except socket.gaierror, err:
        print "cannot resolve hostname: ", name, err
        
    
    # Create a process for each BeagleBone
    try:
        for i in range(numRelayStat):
            streamingProcs.append(multiprocessing.Process(target = stream.stream_process, args=(ports[i], useAccel[i], useLight[i], useADC[i])))
    except:
        print "Error reading config file: incorrect parameters for relay stations"
    
    for proc in streamingProcs:  
        proc.start()
   
    for proc in streamingProcs:  
        proc.join()