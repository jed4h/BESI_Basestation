import random

TOTAL_ROOMS = 3 # possible rooms 0, 1, or 2
START_ROOM = 0
TOTAL_TIME = 50

P_LEAVE = 0.3 # probability of leaving a room during a given timestep

P_CHANGE_CONNECT = 0.8  # probability that the connection will switch to the correct room
P_DS_TRIGGER = 0.95 # porbability that the door sensor will generate a true positive

transition = 0

connected_data = open("connectionData", "w")
door_sensor_data0 = open("doorData0", "w")
door_sensor_data1 = open("doorData1", "w")
door_sensor_data2 = open("doorData2", "w")
actual_room = open("actualRoom", "w")

#connected_data.write("{}\n".format(START_ROOM))
current_room = START_ROOM
next_room = START_ROOM
connected_room = current_room

for i in range(TOTAL_TIME):
    
        
    if random.uniform(0,1) < P_LEAVE: # leaving current room
        transition = 1;
        # pick a new room
        while current_room == next_room:
            next_room = random.randint(0,2)
        if current_room == 0: # leaving room 0
            door_sensor_data0.write("{}\n".format(-1))
        elif current_room == 1: # leaving room 1
            door_sensor_data1.write("{}\n".format(-1))
        elif current_room == 2: # leaving room 2
            door_sensor_data2.write("{}\n".format(-1))
     
        
        if next_room == 0: # entering room 0
            door_sensor_data0.write("{}\n".format(1))
            print "moving to room 0"
        elif next_room == 1: # entering room 1
            door_sensor_data1.write("{}\n".format(1))
            print "moving to room 1"
        elif next_room == 2: # entering room 2
            door_sensor_data2.write("{}\n".format(1))
            print "moving to room 2"
            
        #write a 0 if not current or next room
        if current_room != 0 and next_room != 0:
            door_sensor_data0.write("{}\n".format(0))
        if current_room != 1 and next_room != 1:
            door_sensor_data1.write("{}\n".format(0))
        if current_room != 2 and next_room != 2:
            door_sensor_data2.write("{}\n".format(0))     
                
            
    else:
        transition = 0;
        next_room = current_room
        door_sensor_data0.write("{}\n".format(0))
        door_sensor_data1.write("{}\n".format(0))
        door_sensor_data2.write("{}\n".format(0))    
    
    
    actual_room.write("{}\n".format(current_room))
    connected_data.write("{}\n".format(connected_room))
    if transition and random.uniform(0,1) < P_CHANGE_CONNECT:
        connected_room = next_room
    # update current room
    current_room = next_room
    
connected_data.close()
door_sensor_data0.close()
door_sensor_data1.close()
door_sensor_data2.close()
actual_room.close()