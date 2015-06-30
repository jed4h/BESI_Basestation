import stream
import multiprocessing
from parameters import *
import os
import socket
from streamParseConfig import streamParseConfig

if __name__ == '__main__':
    # required to prevent spawning multiple processes when run as an executable
    multiprocessing.freeze_support()
    
    streamingProcs = []
    
    # use a separate folder to save data files
    # if the folder does not exist, create it
    if not os.path.exists("data"):
        os.mkdir("data")
    
    # get parameters from the config file  
    ports, useAccel, useLight, useADC, ShimmerID, PLOT, numRelayStat = streamParseConfig()
               
                
    print "Relay Station IDs: ",ports
    print "Use Accelerometer: ",useAccel
    print "Use Microphone and Temperature Sensor: ",useADC
    print "Use Light Sensor", useLight
    
    # print the host IP address so the user can enter it in the BBB application   
    name = socket.gethostname()   
    try:
        host = socket.gethostbyname(name)
        print "Basestation IP Address: ",host
    except socket.gaierror, err:
        print "cannot resolve hostname: ", name, err
        
    
    # Create a process for each BeagleBone
    try:
        for i in range(numRelayStat):
            streamingProcs.append(multiprocessing.Process(target = stream.stream_process, args=(ports[i], useAccel[i], useLight[i], useADC[i], ShimmerID, PLOT)))
    except:
        print "Error reading config file: incorrect parameters for relay stations"
    
    for proc in streamingProcs:  
        proc.start()
   
    for proc in streamingProcs:  
        proc.join()