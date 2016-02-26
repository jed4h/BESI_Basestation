import Tkinter as tk
import tkFileDialog
from processAccel import plotAccel
from localizationUtils import *



# key = "entryRoom" + "exitRoom". if exit_room_ID < entry_room_ID, sign of value is flipped.
# index on inner arrays is relay station ID
#expectedRSSIChange = {"12":[1,-1,1,0], "13":[1,1,-1,1], "14":[1,0,1,-1], "04":[-1,-1,-1,-1]}
#expectedRSSIChange = {"01":[-1,-1,-1], "31":[-1,-1,1], "21":[-1,1,-1]}
#expectedRSSIChange = {"23":[-1,-1,-1,-1], "34":[0,-1,1,-1], "14":[-1,1,-1,-1], "04":[1,0,1,-1]}
expectedRSSIChange = {"31":[-1,-1,1], "21":[-1,1,-1], "01":[-1,1,-1]}

# total number of states
numStates = 4
maxTime = 650

# identifier for each state
states = (1,2,3,0) 
# rooms with a relay station
relayStats = (1,2,3)  


# format is timestamp:(exitRoom, entryRoom, occupancy, accelerometer activity)
dsData = {63:DoorSensorReading(1,0,2,1),88:DoorSensorReading(0,1,1,0), 175:DoorSensorReading(1,0,2,1), 189:DoorSensorReading(1,0,1,0),
          195:DoorSensorReading(0,1,1,1), 202:DoorSensorReading(0,1,1,1), 
          99:DoorSensorReading(1,2,2,1), 130:DoorSensorReading(1,2,1,1),149:DoorSensorReading(2,1,2,1), 153:DoorSensorReading(2,1,1,1), 
          163:DoorSensorReading(1,2,2,0), 169:DoorSensorReading(2,1,1,0),
          60:DoorSensorReading(1,3,1,1), 87:DoorSensorReading(1,3,1,0), 95:DoorSensorReading(3,1,1,1), 107:DoorSensorReading(3,1,1,0),
          164:DoorSensorReading(1,3,1,0), 167:DoorSensorReading(3,1,1,0)
          }
"""

dsData = {243:DoorSensorReading(1,2,2,1), 281:DoorSensorReading(1,2,1,0), 320:DoorSensorReading(2,1,2,0), 408:DoorSensorReading(2,1,1,1),
          591:DoorSensorReading(1,2,2,0), 625:DoorSensorReading(1,2,1,1), 633:DoorSensorReading(2,1,2,1), 645:DoorSensorReading(2,1,1,0),
          353:DoorSensorReading(1,3,2,0), 389:DoorSensorReading(3,1,1,0), 435:DoorSensorReading(1,3,2,1), 522:DoorSensorReading(3,1,1,1),
          541:DoorSensorReading(1,0,2,0), 574:DoorSensorReading(0,1,1,1)
          }


dsData = {47:DoorSensorReading(4,3,2,0),81:DoorSensorReading(3,4,1,0), 143:DoorSensorReading(4,1,2,1), 188:DoorSensorReading(4,0,1,0),
          207:DoorSensorReading(0,4,1,0), 216:DoorSensorReading(4,1,1,0), 228:DoorSensorReading(1,4,2,1), 233:DoorSensorReading(1,4,1,0),
          257:DoorSensorReading(4,3,2,1), 299:DoorSensorReading(3,4,1,1), 307:DoorSensorReading(4,0,2,1), 308:DoorSensorReading(4,3,1,1),
          314:DoorSensorReading(3,2,1,0), 337:DoorSensorReading(2,3,1,0), 342:DoorSensorReading(3,4,1,0), 362:DoorSensorReading(0,4,1,1)
          }


dsData = {135:DoorSensorReading(1,2,3,1),148:DoorSensorReading(2,1,1,0), 192:DoorSensorReading(1,2,2,1), 204:DoorSensorReading(2,1,1,0),
          268:DoorSensorReading(1,2,3,1), 273:DoorSensorReading(1,2,2,0), 291:DoorSensorReading(2,1,2,1), 309:DoorSensorReading(2,1,1,0),
          330:DoorSensorReading(1,2,3,0), 357:DoorSensorReading(2,1,1,0), 
          139:DoorSensorReading(1,3,2,1), 191:DoorSensorReading(3,1,1,1), 223:DoorSensorReading(1,3,2,0), 251:DoorSensorReading(3,1,1,0),
          317:DoorSensorReading(1,3,3,0), 327:DoorSensorReading(3,1,1,0),
          232:DoorSensorReading(4,0,1,0), 241:DoorSensorReading(0,4,1,0), 343:DoorSensorReading(4,0,1,1), 365:DoorSensorReading(0,4,1,0),
          182:DoorSensorReading(1,4,2,1), 209:DoorSensorReading(4,1,1,0), 227:DoorSensorReading(1,4,2,0), 245:DoorSensorReading(4,1,1,0),
          335:DoorSensorReading(1,4,2,1), 346:DoorSensorReading(1,4,1,1), 381:DoorSensorReading(4,1,2,1), 389:DoorSensorReading(4,1,1,1)
          }

"""
accelProcFile1 = open("Data_Deployment_9/Relay_Station_10014/Accelerometer/Accelerometer_Synched2016-01-14_15-23.txt", "r")
accelProcFile2 = open("Data_Deployment_9/Relay_Station_9999/Accelerometer/Accelerometer_Synched2016-01-14_15-23.txt", "r")
accelProcFile3 = open("Data_Deployment_9/Relay_Station_10004/Accelerometer/Accelerometer_Synched2016-01-14_15-23.txt", "r")
"""

accelProcFile1 = open("Data_Deployment_9/Relay_Station_9999/Accelerometer/Accelerometer_Synched2016-01-14_13-23.txt", "r")
accelProcFile2 = open("Data_Deployment_9/Relay_Station_10004/Accelerometer/Accelerometer_Synched2016-01-14_13-23.txt", "r")
accelProcFile3 = open("Data_Deployment_9/Relay_Station_10009/Accelerometer/Accelerometer_Synched2016-01-14_13-23.txt", "r")
accelProcFile4 = open("Data_Deployment_9/Relay_Station_10014/Accelerometer/Accelerometer_Synched2016-01-14_13-23.txt", "r")

accelProcFile2 = open("Data_Deployment_9/Relay_Station_9999/Accelerometer/Accelerometer_Synched2016-01-14_13-06.txt", "r")
accelProcFile3 = open("Data_Deployment_9/Relay_Station_10004/Accelerometer/Accelerometer_Synched2016-01-14_13-06.txt", "r")
accelProcFile1 = open("Data_Deployment_9/Relay_Station_10009/Accelerometer/Accelerometer_Synched2016-01-14_13-06.txt", "r")

accelProcFile2 = open("Data_Deployment_9/Relay_Station_9999/Accelerometer/Accelerometer_Synched2016-01-14_15-14.txt", "r")
accelProcFile3 = open("Data_Deployment_9/Relay_Station_10004/Accelerometer/Accelerometer_Synched2016-01-14_15-14.txt", "r")
accelProcFile4 = open("Data_Deployment_9/Relay_Station_10009/Accelerometer/Accelerometer_Synched2016-01-14_15-14.txt", "r")
accelProcFile1 = open("Data_Deployment_9/Relay_Station_10014/Accelerometer/Accelerometer_Synched2016-01-14_15-14.txt", "r")
"""





doorData = []
probDSChange = []

transProb = [[[0]*numStates] for i in range(numStates)]
locProb = [[0]*numStates for i in range(maxTime)]



root = tk.Tk()
root.withdraw()

#print "Select an accelerometer file to plot"
#fname1 = tkFileDialog.askopenfilename()



#if fname1 != None:
    #accelProcFile = open(fname1, "r")
    #accelProcFile = open("data/Accelerometer2015-07-06_15-18", "r")
t_data1, x_data, y_data, z_data, rssi_data1 = plotAccel(accelProcFile1)
for i in range(len(rssi_data1)):
    if rssi_data1[i] == 0 and x_data[i] == 0:
        rssi_data1[i] = -200
    
    if rssi_data1[i] < -200:
        rssi_data1[i] = -200
        
t_data2, x_data, y_data, z_data, rssi_data2 = plotAccel(accelProcFile2)
for i in range(len(rssi_data2)):
    if rssi_data2[i] == 0 and x_data[i] == 0:
        rssi_data2[i] = -200
    
    if rssi_data2[i] < -200:
        rssi_data2[i] = -200
        
t_data3, x_data, y_data, z_data, rssi_data3 = plotAccel(accelProcFile3)
for i in range(len(rssi_data3)):
    if rssi_data3[i] == 0 and x_data[i] == 0:
        rssi_data3[i] = -200
    
    if rssi_data3[i] < -200:
        rssi_data3[i] = -200

"""     
t_data4, x_data, y_data, z_data, rssi_data4 = plotAccel(accelProcFile4)
for i in range(len(rssi_data4)):
    if rssi_data4[i] == 0 and x_data[i] == 0:
        rssi_data4[i] = -200
    
    if rssi_data4[i] < -200:
        rssi_data4[i] = -200
"""

for i in range(numStates):
        locProb[0][i] = 1.0/numStates
        

for t in range(maxTime)[1:]:
    for i in range(numStates):
        locProb[t][i] = locProb[t-1][i]
        
    scaleF = 1
    
    # check if an door sensor was triggered in that second
    if t in dsData:
        entRoom = dsData[t].entryRoom
        exRoom = dsData[t].exitRoom
        
        # get the expected direction of the change in RSSI
        if (str(entRoom) + str(exRoom)) in expectedRSSIChange:
            RSSIDir = expectedRSSIChange[str(entRoom) + str(exRoom)]
        else:
            RSSIDir = expectedRSSIChange[str(exRoom) + str(entRoom)]
            scaleF = -1
        
        rssi1 = getRSSIChange(t_data1, t, rssi_data1, scaleF * RSSIDir[0], False)
        rssi2 = getRSSIChange(t_data2, t, rssi_data2, scaleF * RSSIDir[1], True)
        rssi3 = getRSSIChange(t_data3, t, rssi_data3, scaleF * RSSIDir[2], False)
        #rssi4 = getRSSIChange(t_data4, t, rssi_data4, scaleF * RSSIDir[3], True)
        rssi = max(rssi1, rssi2, rssi3)

        #probChange = ((rssi + dsData[t].accel) + locProb[t-1][exRoom]/dsData[t].occupancy)/2
        probChange = ((rssi + dsData[t].accel))/2
        if probChange > 0.9:
            probChange = 0.9
        
        
        probDSChange.append([t, rssi, dsData[t].accel, locProb[t-1][exRoom]/dsData[t].occupancy, probChange])
        dsData[t].probPWD = probChange
        pStay = (1-probChange)
        for j in range(numStates):
            if j == entRoom:
                locProb[t][entRoom] = probChange + pStay*locProb[t-1][entRoom]
            else:
                locProb[t][j] = pStay*locProb[t-1][j]


print probDSChange



roomLocations = []
      
location_sequence = viterbi(maxTime, dsData, states, relayStats)

for t in range(maxTime):
    if t in dsData:
        print t, location_sequence[t-1],location_sequence[t], location_sequence[t+1]




        