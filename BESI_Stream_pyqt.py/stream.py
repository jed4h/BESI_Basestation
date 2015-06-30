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


# receives data from the BBB using a different socket for each sensor
# the port number for the accelerometer is given, and the other sockets are consecutive numbers following PORT
def stream_process(PORT = 9999, USE_ACCEL = True, USE_LIGHT = True, USE_ADC = True, ShimmerID = "94:A0", PLOT=True):
    t = []
    x = []
    y = []
    z = []
    light = []
    sound = []
    temp = []
    sound_sum = []
   
    # temporary files to hold the raw data for each sensor
    faccel = open("data/accel{}".format(PORT), "w")
    flight = open("data/light{}".format(PORT + 1), "w")
    soundFile = open("data/sound{}".format(PORT + 2), "w")
    tempFile = open("data/temp{}".format(PORT + 3), "w")
    
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
        configMsg = "{},{},{},{},".format(USE_ACCEL, USE_ADC, USE_LIGHT, ShimmerID)
        connection.sendall("{:03}".format(len(configMsg)) + configMsg)
        connection.close()
    except:
        pass
    
    # establish socket connections for each sensor used
    if USE_ACCEL:
        connection = connectRecv(PORT)
    else:
        connection = None
        
    if USE_LIGHT:
        connection2 = connectRecv(PORT + 1)
    else:
        connection2 = None
        
    if USE_ADC:
        connection3 = connectRecv(PORT + 2)
        connection4 = connectRecv(PORT + 3)
    else:
        connection3 = None
        connection4 = None
    
    
    app = QtGui.QApplication([])
    if PLOT:
        win, curves = init_plot()
        
    
    
    # update is called every 5 ms and updates the data for each plot
    def update():
        plot_update_all(connection, connection2, connection3, connection4, faccel, flight, soundFile, tempFile, t, x, y ,z, light, sound, sound_sum, temp, USE_ACCEL, USE_LIGHT, USE_ADC)
        if PLOT:
            curves[0].setData(x)
            curves[1].setData(y)
            curves[2].setData(z)
            curves[3].setData(t)
            curves[4].setData(light)
            curves[5].setData(sound)
            curves[7].setData(temp)
        
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
    
# runs update functions for each sensor used
# update functions check if data is ready and update the plot ifit is
#con1 = accel, con2 = light, con3 = sound, con4 = temp
def plot_update_all(con1, con2, con3, con4, faccel, flight, soundFile, tempFile, t, x, y ,z, light, sound, sound_sum, temp, USE_ACCEL, USE_LIGHT, USE_ADC):
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