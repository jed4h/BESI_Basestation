# functions used for BBB streaming application
import socket
import sys
import pyqtgraph as pg
from datetime import datetime

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

# returns the average of value of data
def moving_avg(data):
    avg = 0
    if len(data) > 0:
        avg = float(sum(data))/len(data)
    return avg

# check connection for data up to BufSize in length and return it if present
# TODO: what happened to peeking to see the amount of data available
def recv_nonblocking(connection, bufSize):
    connection.settimeout(0)
    try:
        data = connection.recv(bufSize)
    except:
        data = None
        
    return data

# append new_data to array and remove the oldest piece of data from array if the length of array is greater than max_size 
def append_fixed_size(array, new_data, max_size):
    array.append(new_data)
    if len(array) > max_size:
            array.pop(0)
            
# parses values for timestamp, x-axis, y-axis, and z-axis from string in csv format            
def parse_accel(raw_data):
    # index part of each packet we are processing
    index = 0
    data = []
    for element in raw_data.split(","):
        # if data cannot be cast as an int, it is something other than data
        try:
            (int(element))
        except:
            data.append(None)
        else:
            # format is <timestamp>,<x-axis>,<y-axis>,<z-axis>,\n
            if index == 0:
                # timestamp is the number of ticks of a 32768 Hz clock
                # sampling at 51.2 Hz means 640 ticks per sample
                data.append(int(element)/640)
                index = 1             
            elif index == 1:
                data.append(int(element))
                index = 2
            elif index == 2:
                data.append(int(element))
                index = 3
            else:
                data.append(int(element))
                index = 0
     
    return data

# parses values for timestamp, degree C, degree F from string in csv format
# for plotting we only care about the degree F because the time axis is in samples                 
def parse_temp(raw_data):
    split_data = raw_data.split(",")
    try:
        # if degree F cannot be case to a float, the line is not data
        data = float(split_data[2])
    except:
        data = None
        
    return data

# parses values for timestamp, noise level from string in csv format
# for plotting we only care about the noise level because the time axis is in samples
# noise level is the sum of the amplitudes in volts(rails are +-0.9V) of 100 samples with a sampling rate of 10kHz
def parse_sound(raw_data):
    split_data = raw_data.split(",")
    try:
        # if noise level cannot be case to a float, the line is not data
        data = float(split_data[1])
    except:
        data = None
        
    return data

# parses values for timestamp, light level from string in csv format
# for plotting we only care about the light level because the time axis is in samples
def parse_light(raw_data):
    element = raw_data.split(",")
    try:
        # if light level cannot be case to a float, the line is not data
        data = (float(element[1]))
    except:
        data = None
            
    return data

# listen at the given port for a connection, and return it if one is made
def connectRecv(port):
    # configuration parameters; purpose unknown
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the port
    server_address = (socket.gethostname(), port)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    
    # Listen for incoming connections
    sock.listen(1)
    
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()
    
    print >>sys.stderr, 'connection from', client_address
    # make connection nonblocking
    connection.settimeout(0)
    
    return connection

# check if accelerometer data is ready
def update_accel(connection, outFile, t, x, y, z):
    # each accelerometer packet is 22 bytes long
    # check if two packets are rady
    data = recv_nonblocking(connection, 44)
    if data != None:
        # save received data
        outFile.write(data)
        split_data = parse_accel(data)
        # add data to arrays
        if split_data[0] != None:
            append_fixed_size(t, split_data[0], 200)
            append_fixed_size(x, split_data[1], 200)
            append_fixed_size(y, split_data[2], 200)
            append_fixed_size(z, split_data[3], 200)
    
    
        try:
            #check for all 0s, which signals a lost connection
            if t[-1] == 0 and x[-1] == 0 and y[-1] == 0 and z[-1] == 0:
                # write time so that the duration of connection loss can be detirmined
                outFile.write(str(datetime.now()) + '\n')
        except:
            pass      
       

# check if light data is ready
def update_light(connection, outFile, light):
    # each packet is 25 bytes
    data = recv_nonblocking(connection, 25)
    if data != None:
        outFile.write(data)
        split_data = parse_light(data)
        if split_data != None:
            append_fixed_size(light, split_data, 200)


# check if sound data is ready    
def update_sound(connection, outFile, sound, sound_sum):
    # each packet is 23 bytes
    data = recv_nonblocking(connection, 23)
    if data != None:
        outFile.write(data)
        split_data = parse_sound(data)
        if split_data != None:
            # noise data is plotted over 1000 semples = 10 seconds
            append_fixed_size(sound, split_data, 1000)
            
            # moving average - no longer used
            to_avg = sound
            if len(sound) > 100:
                to_avg = sound[len(sound) - 100:]
                
            append_fixed_size(sound_sum, moving_avg(to_avg), 1000)
            

# check if temperature data is ready    
def update_temp(connection, outFile, temp):
    # size of a temperature data packet is 20 bytes
    data = recv_nonblocking(connection, 20)
    if data != None:
        outFile.write(data)
        split_data = parse_temp(data)
        if split_data != None:
            append_fixed_size(temp, split_data, 200)
        
# initialize plots    
def init_plot():
    curves = []
    win = pg.GraphicsWindow(title="Accelerometer data")
    win.resize(1000,600)
    win.setWindowTitle('Data from Relay Station')
    
    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)
    
    # graph titles
    # TODO: add axis titles
    p1 = win.addPlot(title="Accelerometer")
    p2 = win.addPlot(title="Light")
    win.nextRow()
    p3 = win.addPlot(title="Noise")
    p4 = win.addPlot(title="Temperature")
    
    # ranges for each graph
    p1.setXRange(0, 200)
    p1.setYRange(0,4096)
    p2.setXRange(0, 200)
    p2.setYRange(0,1000)
    p3.setXRange(0, 1000)
    p3.setYRange(0,40)
    p4.setXRange(0, 200)
    p4.setYRange(30,100)
    
    # create a array of curve handlers to return
    curves.append(p1.plot(pen=(255,0,0), name="X-Axis"))
    curves.append(p1.plot(pen=(0,255,0), name="Y_Axis"))
    curves.append(p1.plot(pen=(0,0,255), name="Z_Axis"))
    curves.append(p1.plot(pen=(255,255,255), name="Timestamp"))
    
    curves.append(p2.plot(pen='y', name="Lux"))
    
    curves.append(p3.plot(pen = (0, 255, 0), name="Noise"))
    curves.append(p3.plot(pen = (255, 0, 0), name="Noise_Avg"))
    curves.append(p4.plot(pen=(255,0,0), name="temperature"))
    
    return win, curves