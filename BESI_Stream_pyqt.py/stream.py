# the stream_process function receives and plots sensor data from a single BBB
from datetime import datetime
from pyqtgraph.Qt import QtGui, QtCore
from stream_utils import *
from parameters import PLOT
from BikeCadence import peakDetection


# receives data from the BBB using a different socket for each sensor
# the port number for the accelerometer is given, and the other sockets are consecutive numbers following PORT
def stream_process(PORT = 9999, USE_ACCEL = True, USE_LIGHT = True, USE_ADC = True):
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
    faccel.write(str(datetime.now()) + '\n')
    faccel.close()
    flight.close()
    soundFile.close()
    tempFile.close()