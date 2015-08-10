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
    
    # get parameters from the config file  
    ports, useAccel, useLight, useADC, ShimmerID1, ShimmerID2, ShimmerID3, PLOT, numRelayStat, fileLengthSec, fileLengthDay, DeploymentID = streamParseConfig()
               
    # Create a file structure to hold data for this deployment
    data_folder = "Data_Deployment_{}/".format(DeploymentID)
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)
        
    
    
    # Create folders for each sensor
    for relay_stat in ports:
        relay_station_folder = data_folder + "Relay_Station_{}/".format(relay_stat)
        if not os.path.exists(relay_station_folder):
            os.mkdir(relay_station_folder)  
        if not os.path.exists(relay_station_folder + "Accelerometer"):
            os.mkdir(relay_station_folder + "Accelerometer")
        if not os.path.exists(relay_station_folder + "Temperature"):
            os.mkdir(relay_station_folder + "Temperature")
        if not os.path.exists(relay_station_folder + "Light"):
            os.mkdir(relay_station_folder + "Light")
        if not os.path.exists(relay_station_folder + "Audio"):
            os.mkdir(relay_station_folder + "Audio")
        if not os.path.exists(relay_station_folder + "Door"):
            os.mkdir(relay_station_folder + "Door")
                
    print "Relay Station IDs: ",ports
    print "Use Accelerometer: ",useAccel
    print "Use Microphone and Temperature Sensor: ",useADC
    print "Use Light Sensor", useLight
    
    # print the host IP address so the user can enter it in the BBB application
    # If the basestation has 2 IP addresses, assume the second one is the local network that the BBB will connect to
    try:
        name = socket.gethostbyname_ex(socket.gethostname())[-1][1]
    except:
        name = socket.gethostbyname_ex(socket.gethostname())[-1][0]
    try:
        host = socket.gethostbyname(name)
        print "Basestation IP Address: ",host
    except socket.gaierror, err:
        print "cannot resolve hostname: ", name, err
        
    
    # Create a process for each BeagleBone
    try:
        for i in range(numRelayStat):
            streamingProcs.append(multiprocessing.Process(target = stream.stream_process, args=(ports[i], useAccel[i], useLight[i], useADC[i], ShimmerID1, ShimmerID2, ShimmerID3, PLOT, fileLengthSec, fileLengthDay, DeploymentID)))
    except:
        print "Error reading config file: incorrect parameters for relay stations"
    
    for proc in streamingProcs:  
        proc.start()
   
    for proc in streamingProcs:  
        proc.join()
        