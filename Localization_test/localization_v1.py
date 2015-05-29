class Room(object):
    
    def __init__(self, roomID, connectedRooms, totalRooms, initialProb):
        self.ID = roomID
        self.connectedRooms = connectedRooms
        self.door_sensor_data = []
        self.transProb = [0] * totalRooms       # probability of leaving the current room and moving to room i
        self.locProb = []
        self.locProb.append(initialProb)                   # probability of being in this room
        
        
    def get_room_id(self):
        return self.roomID
    
    # assumes data is set in chronological order
    def set_sensor_data(self, sensorValue):
        self.door_sensor_data.append(sensorValue)
        
    def get_sensor_data(self, time):
        return self.door_sensor_data[time]
    
    def get_transProb(self, i):
        return self.transProb[i]
    
    def set_transProb(self, i, value):
        self.transProb[i] = value
    
    def get_locProb(self, time):
        return self.locProb[time]
    
    def set_locProb(self, value):
        self.locProb.append(value)
    

location = []
connections = []
room_list = []

NUM_ROOMS = 3
 
connected_data = open("connectionData", "r")
door_sensor_data0 = open("doorData0", "r")
door_sensor_data1 = open("doorData1", "r")
door_sensor_data2 = open("doorData2", "r")
predicted_location = open("location", "w")

for i in range(NUM_ROOMS):
    room0 = Room(0, [1,2], 3, 1)
    room1 = Room(1, [0,2], 3, 0)
    room2 = Room(2, [0,1], 3, 0)

for line in door_sensor_data0:
    room0.set_sensor_data(int(line))
    
for line in door_sensor_data1:
    room1.set_sensor_data(int(line))
    
for line in door_sensor_data2:
    room2.set_sensor_data(int(line))
    
for line in connected_data:
    connections.append(int(line))

current_room = connections[0]

for time in range(49):
    #initialize door sensor values
    
    DS00 = 0
    DS01 = 0
    DS02 = 0
    
    DS10 = 0
    DS11 = 0
    DS12 = 0
    
    DS20 = 0
    DS21 = 0
    DS22 = 0
    
    if room0.get_sensor_data(time) != 0 or room1.get_sensor_data(time) != 0 or room2.get_sensor_data(time) != 0:
        
        
        
        
        # calculate the transition probabilities
        if room0.get_sensor_data(time) == -1:
            if room0.get_sensor_data(time + 1) == 1: 
                DS00 = 0.7
            elif room1.get_sensor_data(time + 1) == 1:
                DS01 = 0.7                                  
            elif room2.get_sensor_data(time + 1) == 1:                                
                DS02 = 0.7
                
        if room1.get_sensor_data(time) == -1:
            if room0.get_sensor_data(time + 1) == 1: 
                DS10 = 0.7
            elif room1.get_sensor_data(time + 1) == 1:
                DS11 = 0.7                                  
            elif room2.get_sensor_data(time + 1) == 1:                                
                DS12 = 0.7
                
        if room2.get_sensor_data(time) == -1:
            if room0.get_sensor_data(time + 1) == 1: 
                DS20 = 0.7
            elif room1.get_sensor_data(time + 1) == 1:
                DS21 = 0.7                                  
            elif room2.get_sensor_data(time + 1) == 1:                                
                DS22 = 0.7
                
                
        if connections[time] == connections[time + 1]:
            if connections[time] == 0:
                DS00 += 0.3
            elif connections[time] == 1:
                DS11+= 0.3
            elif connections[time] == 2:
                DS22 += 0.3
            
        else:
            if connections[time] == 0:
                if connections[time + 1] == 1:
                    DS01 += 0.3
                elif connections[time + 1] == 2:
                    DS02 += 0.3
                    
            elif connections[time] == 1:
                if connections[time + 1] == 0:
                    DS10 += 0.3
                elif connections[time + 1] == 2:
                    DS12 += 0.3
                    
            elif connections[time] == 2:
                if connections[time + 1] == 0:
                    DS20 += 0.3
                elif connections[time + 1] == 1:
                    DS21 += 0.3
    
        room0.set_transProb(0, room0.get_locProb(time) * DS00)
        room0.set_transProb(1, room0.get_locProb(time) * DS01)
        room0.set_transProb(2, room0.get_locProb(time) * DS02)
        
        room1.set_transProb(0, room1.get_locProb(time) * DS10)
        room1.set_transProb(1, room1.get_locProb(time) * DS11)
        room1.set_transProb(2, room1.get_locProb(time) * DS12)
        
        room2.set_transProb(0, room2.get_locProb(time) * DS20)
        room2.set_transProb(1, room2.get_locProb(time) * DS21)
        room2.set_transProb(2, room2.get_locProb(time) * DS22)
        
        probEnterR0 = room0.get_transProb(0) + room1.get_transProb(0) + room2.get_transProb(0)
        probExitR0 = room0.get_transProb(0) + room0.get_transProb(1) + room0.get_transProb(2)
        
        probEnterR1 = room0.get_transProb(1) + room1.get_transProb(1) + room2.get_transProb(1)
        probExitR1 = room1.get_transProb(0) + room1.get_transProb(1) + room1.get_transProb(2)
        
        probEnterR2 = room0.get_transProb(2) + room1.get_transProb(2) + room2.get_transProb(2)
        probExitR2 = room2.get_transProb(0) + room2.get_transProb(1) + room2.get_transProb(2)
        
        room0.set_locProb(room0.get_locProb(time) - probExitR0 + probEnterR0)
        room1.set_locProb(room1.get_locProb(time) - probExitR1 + probEnterR1)
        room2.set_locProb(room2.get_locProb(time) - probExitR2 + probEnterR2)
    
    else:
        room0.set_locProb(room0.get_locProb(time))
        room1.set_locProb(room1.get_locProb(time))
        room2.set_locProb(room2.get_locProb(time))
    
    #print "time: {}".format(time + 1)    
    #print "locProb room 0 = {}".format(room0.get_locProb(time + 1))
    #print "locProb room 1 = {}".format(room1.get_locProb(time + 1))
    #print "locProb room 2 = {}".format(room2.get_locProb(time + 1))
    
    
    predicted_location.write("{0} {1:0.2f} {2:0.2f} {3:0.2f}\n".format(time + 1,
                                                        room0.get_locProb(time + 1), 
                                                        room1.get_locProb(time + 1), 
                                                        room2.get_locProb(time + 1)))
    
    
    
connected_data.close()
door_sensor_data0.close()
door_sensor_data1.close()
door_sensor_data2.close()
predicted_location.close()