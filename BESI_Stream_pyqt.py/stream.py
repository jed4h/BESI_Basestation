# the stream_process function receives and plots sensor data from a single BBB
from datetime import datetime
from pyqtgraph.Qt import QtGui, QtCore
from streamUtils import *
from parameters import *
from BikeCadence import peakDetection
from streamAccel import update_accel
from streamLight import update_light
from streamSound import update_sound
from streamTemp import update_temp
from streamDoor import update_door
from processSession import processSession


faccel = None
soundFile = None
tempFile = None
doorFile = None
flight = None
plotStartTime = None
sensorTimeouts = [0] * 5 #tracks time since last packet received for each sensor

# receives data from the BBB using a different socket for each sensor
# the port number for the accelerometer is given, and the other sockets are consecutive numbers following PORT
def stream_process(PORT = 9999, USE_ACCEL = True, USE_LIGHT = True, USE_ADC = True, ShimmerID1 = "94:A0", ShimmerID2 = "94:A0", ShimmerID3 = "94:A0", PLOT=True, fileLengthSec = 600, fileLengthDay = 0, DeploymentID = 1):
    global faccel
    global soundFile
    global tempFile
    global doorFile
    global flight
    global plotStartTime
    global sensorTimeouts
    t = []
    x = []
    y = []
    z = []
    light = []
    sound = []
    temp = []
    sound_sum = []
    door1 = []
    door2 = []
    
   
    # write start time
    # Now done in stream when data is first received
    #faccel.write(str(datetime.now()) + '\n')
    #flight.write(str(datetime.now()) + '\n')
    #soundFile.write(str(datetime.now()) + '\n')
    #tempFile.write(str(datetime.now()) + '\n')
    
    # send info to the BBB: Shimmer Bluetooth ID and what sensors to use
    # this uses the same port as the accelerometer and closes it after sending the info
    try:
        connection = connectRecv(PORT)
        configMsg = "{},{},{},{},{},{},".format(USE_ACCEL, USE_ADC, USE_LIGHT, ShimmerID1, ShimmerID2, ShimmerID3)
        connection.sendall("{:03}".format(len(configMsg)) + configMsg)
        connection.close()
    except:
        pass
    
    # establish socket connections for each sensor used
    if USE_ACCEL:
        connection = connectRecv(PORT)
        faccel = open("Data_Deployment_{}/relay_Station_{}/accel{}".format(DeploymentID, PORT, PORT), "w")
    else:
        connection = None
        
    if USE_LIGHT:
        connection2 = connectRecv(PORT + 1)
        flight = open("Data_Deployment_{}/relay_Station_{}/light{}".format(DeploymentID, PORT, PORT), "w")
    else:
        connection2 = None
        
    if USE_ADC:
        connection3 = connectRecv(PORT + 2)
        connection4 = connectRecv(PORT + 3)
        connection5 = connectRecv(PORT + 4)
        soundFile = open("Data_Deployment_{}/relay_Station_{}/sound{}".format(DeploymentID, PORT, PORT), "w")
        tempFile = open("Data_Deployment_{}/relay_Station_{}/temp{}".format(DeploymentID, PORT, PORT), "w")
        doorFile = open("Data_Deployment_{}/relay_Station_{}/door{}".format(DeploymentID, PORT, PORT), "w")
    else:
        connection3 = None
        connection4 = None
        connection5 = None
    
    
    app = QtGui.QApplication([])
    if PLOT:
        win, curves = init_plot(PORT)
        
    plotStartTime = datetime.now()
    
    # update is called every 5 ms and updates the data for each plot
    def update():
        global faccel
        global soundFile
        global tempFile
        global doorFile
        global flight
        global plotStartTime
        global sensorTimeouts
        
        plotCurrTime = datetime.now()
        if ((plotCurrTime - plotStartTime).seconds == fileLengthSec) and ((plotCurrTime - plotStartTime).days == fileLengthDay):
            print "Bingo."
            plotStartTime = datetime.now()
            if USE_ACCEL:
                faccel.close()
                
            if USE_ADC:
                soundFile.close()
                tempFile.close()
                doorFile.close()
                
            if USE_LIGHT:
                flight.close()
            
            processSession(PORT)
            
            if USE_ACCEL:
                faccel = open("Data_Deployment_{}/relay_Station_{}/accel{}".format(DeploymentID, PORT, PORT), "w")
                
            if USE_ADC:
                soundFile = open("Data_Deployment_{}/relay_Station_{}/sound{}".format(DeploymentID, PORT, PORT), "w")
                tempFile = open("Data_Deployment_{}/relay_Station_{}/temp{}".format(DeploymentID, PORT, PORT), "w")
                doorFile = open("Data_Deployment_{}/relay_Station_{}/door{}".format(DeploymentID, PORT, PORT), "w")
                
            if USE_LIGHT:
                flight = open("Data_Deployment_{}/relay_Station_{}/light{}".format(DeploymentID, PORT, PORT), "w")
            
        plot_update_all(connection, connection2, connection3, connection4, connection5, faccel, flight, soundFile, tempFile, doorFile, t, x, y ,z, light, sound, sound_sum, temp, door1, door2, sensorTimeouts, USE_ACCEL, USE_LIGHT, USE_ADC)
        if PLOT:
            curves[0].setData(x)
            curves[1].setData(y)
            curves[2].setData(z)
            curves[3].setData(t)
            curves[4].setData(light)
            curves[5].setData(sound)
            curves[7].setData(temp)
            curves[8].setData(door1)
            curves[9].setData(door2)
        
        # application that prints the cadence of someone biking       
        if BIKE_CADENCE:
            # intervals is meaningless because only raw timestamps are available
            pedal_count, intervals = peakDetection(x[120:], y[120:], t[120:])
            print pedal_count
    
    # set up a timer to run update() every 5 ms   
    timer1 = QtCore.QTimer()
    timer1.timeout.connect(update)
    timer1.start(5)
    
    # keeps the program running while the plot window is open
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    
    # cleanup: close files and write end time to accel file
    # I don't think this code is ever called
    # TODO: find a way to close the files when done
    faccel.write(str(datetime.now()) + '\n')
    faccel.close()
    flight.close()
    soundFile.close()
    tempFile.close()
    processSession(PORT)
    print "Exiting {}".format(PORT)
    
# runs update functions for each sensor used
# update functions check if data is ready and update the plot ifit is
#con1 = accel, con2 = light, con3 = sound, con4 = temp
def plot_update_all(con1, con2, con3, con4, con5, faccel, flight, soundFile, tempFile, doorFile, t, x, y ,z, light, sound, sound_sum, temp, door1, door2, sensorTimeouts, USE_ACCEL, USE_LIGHT, USE_ADC):
    # sensorTimeouts is used to to check if no messages have been received about a particular sensor for a period of time 
    # every time update_<sensor> is called and there is no data waiting sensorTimeout is incremented. When sensorTimeout reaches somethreshold, an alert is triggered
    # update accel
    if USE_ACCEL:
        update_accel(con1, faccel, t, x, y, z)
         
    # update light
    if USE_LIGHT:
        update_light(con2, flight, light)

    # update ADC (noise and temp)
    if USE_ADC:
        update_sound(con3, soundFile, sound, sound_sum)
        update_temp(con4, tempFile, temp)
        update_door(con5, doorFile, door1, door2)
    """
    if USE_ACCEL:
        if (update_accel(con1, faccel, t, x, y, z) == 1):
            sensorTimeouts[0] = sensorTimeouts[0] + 1
            
        else:
            sensorTimeouts[0] = 0
            
        if sensorTimeouts[0] == LOST_CONN_TIMEOUT:
            #print "Accel Message",datetime.now()
            sensorTimeouts[0] = 0
        
    # update light
    if USE_LIGHT:
        if (update_light(con2, flight, light) == 1):
            sensorTimeouts[1] = sensorTimeouts[1] + 1
            
        else:
            sensorTimeouts[1] = 0
            
        if sensorTimeouts[1] == LOST_CONN_TIMEOUT:
            #print "Light Message"
            sensorTimeouts[1] = 0
        
    # update ADC (noise and temp)
    if USE_ADC:
        if (update_sound(con3, soundFile, sound, sound_sum) == 1):
            sensorTimeouts[2] = sensorTimeouts[2] + 1   
        else:
            sensorTimeouts[2] = 0
        if sensorTimeouts[2] == LOST_CONN_TIMEOUT:
            #print "Sound Message"
            sensorTimeouts[2] = 0
            
        if (update_temp(con4, tempFile, temp) == 1):
            sensorTimeouts[3] = sensorTimeouts[3] + 1
        else:
            sensorTimeouts[3] = 0 
        if sensorTimeouts[3] == LOST_CONN_TIMEOUT:
            #print "Temperature Message"
            sensorTimeouts[3] = 0
            
        if (update_door(con5, doorFile, door1, door2) == 1):
            sensorTimeouts[4] = sensorTimeouts[4] + 1 
        else:
            sensorTimeouts[4] = 0 
        if sensorTimeouts[4] == LOST_CONN_TIMEOUT:
            #print "Door Message" 
            sensorTimeouts[4] = 0
            """

