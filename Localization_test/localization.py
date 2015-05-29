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
        
        
def get_tprobs(room_list, numRooms, time, connections):
    tprob = [[0]*numRooms for i in range(numRooms)]
    change = 0
    
    # check if any of the door sensors has detected movement
    for room in room_list:
        if room.get_sensor_data(time) != 0:
            change = 1
            break
    
    # look for a transition from room i to room j
    # as indicated by someone leaving room i and entering room j
    if change == 1:
        for i in range(numRooms):
            if room_list[i].get_sensor_data(time) == -1:
                for j in range(numRooms):
                    if room_list[j].get_sensor_data(time) == 1: 
                        tprob[i][j] = 0.7
        
        # if the connection stays the same, update the probability of staying in that room                                  
        if connections[time] == connections[time + 1]:
            for i in range(numRooms):
                tprob[i][i] += 0.3
        
        # if the connection changes look for a transition from room i to room j       
        else:
            for i in range(numRooms):
                for j in range(numRooms):
                    if connections[time] == i and connections[time + 1] == j:
                        tprob[i][j] += 0.3
        
    return change, tprob    
    
    
location = []
connections = []
room_list = []

NUM_ROOMS = 3
ROOM_CONNECTIONS = [[1, 2], [0, 2], [0, 1]]
INITIAL_PROBS = [0.33, 0.34, 0.33]
 
connected_data = open("connectionData", "r")
door_sensor_data0 = open("doorData0", "r")
door_sensor_data1 = open("doorData1", "r")
door_sensor_data2 = open("doorData2", "r")
predicted_location0 = open("location0", "w")
predicted_location1 = open("location1", "w")
predicted_location2 = open("location2", "w")

for i in range(NUM_ROOMS):
    room_list.append(Room(i, ROOM_CONNECTIONS[i], NUM_ROOMS, INITIAL_PROBS[i]))

for line in door_sensor_data0:
    room_list[0].set_sensor_data(int(line))
    
for line in door_sensor_data1:
    room_list[1].set_sensor_data(int(line))
    
for line in door_sensor_data2:
    room_list[2].set_sensor_data(int(line))
    
for line in connected_data:
    connections.append(int(line))

current_room = connections[0]

for time in range(49):
    #initialize door sensor values
    
    (change, ds) = get_tprobs(room_list, NUM_ROOMS, time, connections)
    
    if change == 1:
        for i in range(NUM_ROOMS):
            for j in range(NUM_ROOMS):
                room_list[i].set_transProb(j, room_list[i].get_locProb(time) * ds[i][j]) 
                
        enterProb = [0]*NUM_ROOMS
        exitProb = [0]*NUM_ROOMS
        
        for i in range(NUM_ROOMS):
            for j in range(NUM_ROOMS):
                # look for transitions from room j to room i
                enterProb[i] += room_list[j].get_transProb(i)
                # look for transitions from room i to room j
                exitProb[i] += room_list[i].get_transProb(j)
        
        for i in range(NUM_ROOMS):
            room_list[i].set_locProb(room_list[i].get_locProb(time) - exitProb[i] + enterProb[i])
    
    else:
        for room in room_list:
            room.set_locProb(room.get_locProb(time))
    
    #print "time: {}".format(time + 1)    
    #print "locProb room 0 = {}".format(room0.get_locProb(time + 1))
    #print "locProb room 1 = {}".format(room1.get_locProb(time + 1))
    #print "locProb room 2 = {}".format(room2.get_locProb(time + 1))
    
    
    predicted_location0.write("{0} {1:0.2f} {2:0.2f} {3:0.2f}\n".format(time + 1,
                                                        room_list[0].get_locProb(time + 1), 
                                                        room_list[1].get_locProb(time + 1), 
                                                        room_list[2].get_locProb(time + 1)))
    
    
    
connected_data.close()
door_sensor_data0.close()
door_sensor_data1.close()
door_sensor_data2.close()
predicted_location0.close()