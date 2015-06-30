# functions used for BBB streaming application
import socket
import sys
import pyqtgraph as pg
from datetime import datetime
from parameters import *
import struct

# returns the average of value of data
def moving_avg(data):
    avg = 0
    if len(data) > 0:
        avg = float(sum(data))/len(data)
    return avg

# check connection for data up to BufSize in length and return it if present
def recv_nonblocking(connection, bufSize):
    connection.settimeout(0)
    try:
        data = connection.recv(bufSize)
    except:
        data = None
        
    return data

# check connection for data up to BufSize in length and return it if present
# the first 4 bytes followed by a comma give the length of the payload
def recv_nonblocking_length(connection):
    connection.settimeout(0)
    try:
        header = connection.recv(2)
    except:
        return None
    # we got some data, so wait fort he rest  
    else:
        #print struct.unpack("H", header)
        try:
            #print "waiting for {} bytes of data".format(struct.unpack("H", header)[0])
            #connection.settimeout(1)
            # read until we get a comma
            while(len(header) != 2):
                header = header + connection.recv(2 - len(header))
            
            messageLen = struct.unpack("H", header)[0]
            #messageLen = int(header[:-1])c
            data = ''
            while(len(data) != messageLen):
                data = data + connection.recv(messageLen - len(data))
        
        except:
            print "E"
            return None
        
        else:
            #print "got remaining data"
            return data
    
    
    connection.settimeout(0)
    try:
        header = connection.recv(2)
    except:
        return None
    # we got some data, so wait fort he rest  
    else:
        #print struct.unpack("H", header)
        try:
            #print "waiting for {} bytes of data".format(struct.unpack("H", header)[0])
            #connection.settimeout(1)
            # read until we get a comma
            while(len(header) != 2):
                header = header + connection.recv(2 - len(header))
            
            messageLen = struct.unpack("H", header)[0]
            #messageLen = int(header[:-1])c
            
            data = connection.recv(messageLen)
        
        except:
            print "E"
            return None
        
        else:
            #print "got remaining data"
            if len(data) == messageLen:
                return data
            #else:
                #return None


# append new_data to array and remove the oldest piece of data from array if the length of array is greater than max_size 
def append_fixed_size(array, new_data, max_size):
    array.append(new_data)
    if len(array) > max_size:
            array.pop(0)
            

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