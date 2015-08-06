from parameters import *
from streamUtils import append_fixed_size, recv_nonblocking
from datetime import datetime



# check if accelerometer data is ready
def update_accel(connection, outFile, t, x, y, z):
    # each accelerometer packet is 22 bytes long
    # check if 10 packets are ready
    
    data = recv_nonblocking(connection, 20 * ACCEL_PACKET_SIZE)
    if data != None:
        # if the file is empty, this is the first data received and we need to write the start time
        outFile.seek(0,2)
        if (outFile.tell() == 0):
            outFile.write(str(datetime.now()) + '\n')
        
        # save received data
        # even if we received less than a full 4 packets, the output file will have all the data correctly formatted 
        outFile.write(data)
        
        # raw bytes can be used to reduce bandwidth required
        #split_data = struct.unpack("HHHH", data)
        #outFile.write("{0},{1},{2},{3}\n".format(split_data[0], split_data[1], split_data[2], split_data[3]))
        
        
        split_data = parse_accel(data)
        # add data to arrays
        # this only plots the first packet from every group received, which downsamples by 4
        if (split_data[0] != None):
            append_fixed_size(t, split_data[0], 200)
            append_fixed_size(x, split_data[1], 200)
            append_fixed_size(y, split_data[2], 200)
            append_fixed_size(z, split_data[3], 200)


        try:
            #check for all 0s, which signals a lost connection
            if t[-1] == 0 and x[-1] == 0 and y[-1] == 0 and z[-1] == 0:
                # write time so that the duration of connection loss can be determined
                outFile.write(str(datetime.now()) + '\n')
        except:
            pass    
       

# parses values for timestamp, x-axis, y-axis, and z-axis from string in csv format            
def parse_accel(raw_data):
    # index not needed for this code - maybe change?
    index = 0
    data = []
    #if len(raw_data.split(",")) == 5:
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
                # sampling at 102.4 Hz means 320 ticks per sample
                data.append(int(element)/TICKS_PER_SAMPLE)
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
                    
    #else:
        #data.append(None)
     
    if index != 0:
        data[0] = None
        
    return data