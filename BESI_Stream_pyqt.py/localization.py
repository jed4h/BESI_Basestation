from localizationUtils import *
from datetime import datetime



# key = "entryRoom" + "exitRoom". if exit_room_ID < entry_room_ID, sign of value is flipped.
# index on inner arrays is relay station ID

# 13-23
#expectedRSSIChange = {"12":[1,-1,1,0], "13":[1,1,-1,1], "14":[1,0,1,-1], "04":[-1,-1,-1,-1]}

# 13-06
#expectedRSSIChange = {"01":[-1,0,-1], "31":[-1,-1,1], "21":[-1,1,-1]}

#expectedRSSIChange = {"23":[-1,-1,-1,-1], "34":[0,-1,1,-1], "14":[-1,1,-1,-1], "04":[1,0,1,-1]}
# 15-23
#expectedRSSIChange = {"31":[-1,-1,1], "21":[-1,1,-1], "01":[-1,1,-1]}

# 4-17

expectedRSSIChange = {"21":[-1,-1,-1], "01":[-1,-1,-1], "32":[-1,-1,1]}

# total number of states

maxTime = 40000

# identifier for each state
states = (1,2,3,0)
numStates = len(states) 
# rooms with a relay station
relayStats = (1,2,3)


from localizationUtils import *
import tkFileDialog

    

# settings for 16 9999-10004
"""
window_size = 20
avgRange = 200
peakThreshold = 5

currRoom = 0
nextRoom = 1
goodChannels = 2
"""

window_size = 10
avgRange = 200
peakThreshold = 2
teagThresh = 1000
accel_window_size = 256
magThresh = 0.5
deployID = 16
acceloffset = 10

startDate = "2016-04-17_11-22.txt"

#fname = tkFileDialog.askopenfilename()
fname = "Data_Deployment_" + str(deployID) + "/Relay_Station_9999/Accelerometer/Accelerometer_Synched" + startDate
t_data1, x_data1, y_data1, z_data1 = processAccelFile(fname)

fname = "Data_Deployment_" + str(deployID) + "/Relay_Station_10004/Accelerometer/Accelerometer_Synched" + startDate
t_data2, x_data2, y_data2, z_data2 = processAccelFile(fname)

fname = "Data_Deployment_" + str(deployID) + "/Relay_Station_10009/Accelerometer/Accelerometer_Synched" + startDate
t_data3, x_data3, y_data3, z_data3 = processAccelFile(fname)

"""
# 1-14
#getDSEvents(deployID , relayID, startDateTime, peakThreshold, window_size, avgRange, goodChannels, currRoom, nextRoom)
dsData1 = getDSEvents(9, 9999, startDate, peakThreshold, window_size, avgRange, 1, 1, 2) # room #s flipped
dsData3 = getDSEvents(9, 10014, startDate, peakThreshold, window_size, avgRange, 1, 1, 0)
dsData2 = getDSEvents(9, 10004, startDate, peakThreshold, window_size, avgRange, 2, 3, 1)
"""

dsData1 = getDSEvents(deployID, 10004, startDate, peakThreshold, window_size, avgRange, 2, 1, 0) 
dsData2 = getDSEvents(deployID, 9999, startDate, peakThreshold, window_size, avgRange, 2, 1, 2)
dsData3 = getDSEvents(deployID, 10009, startDate, peakThreshold, window_size, avgRange, 1, 3, 2)


# throws an exception if no file from 10014
try:
    dsData4 = getDSEvents(9, 10014,  startDate, peakThreshold, window_size, avgRange, 1, 1, 4)
except:
    pass

if numStates == 5:
    dsData = combineDSdata([dsData1, dsData2, dsData3, dsData4])
else:
    dsData = combineDSdata([dsData1, dsData2, dsData3])


magData1 = accelCalibMag(x_data1, y_data1, z_data1)
magData2 = accelCalibMag(x_data2, y_data2, z_data2)
magData3 = accelCalibMag(x_data3, y_data3, z_data3)

magVar1 = computeVar(magData1)
magVar2 = computeVar(magData2)
magVar3 = computeVar(magData3)

"""
for i in range(len(magData)/accel_window_size + 1):
        
    try:
        accelTeager.append(teagerCompute(magData[i*accel_window_size:i*accel_window_size + accel_window_size]))
    except:
        accelTeager.append(teagerCompute(magData[i*accel_window_size:-1]))
"""

for transition in dsData.keys():
    # find the indices corresponding to 3 seconds before and 3 seconds after a door transition
    startIndex1 = findAccelIndex(transition - 1 - acceloffset, magData1, t_data1, 1)
    endIndex1 = findAccelIndex(transition + 1- acceloffset, magData1, t_data1, 1)
    
    startIndex2 = findAccelIndex(transition - 1 - acceloffset, magData2, t_data2, 1)
    endIndex2 = findAccelIndex(transition + 1 - acceloffset, magData2, t_data2, 1)
    
    startIndex3 = findAccelIndex(transition - 1 - acceloffset, magData3, t_data3, 1)
    endIndex3 = findAccelIndex(transition + 1 - acceloffset, magData3, t_data3, 1)
    
    #dsData[transition].accel = sum(1 for i in accelTeager[teagerIndex-3:teagerIndex+3] if i > teagThresh)/6.0
    
    magActivity = max(average(magVar1[startIndex1:endIndex1 + 1]), average(magVar2[startIndex2:endIndex2 + 1]), average(magVar3[startIndex3:endIndex3 + 1]))
    
    print transition,magActivity
    if magActivity == 0:
        dsData[transition].accel = 0.5
    elif magActivity > magThresh:
        dsData[transition].accel = 1
    else:
        dsData[transition].accel = 0
    

print "time, entryRoom, exitRoom, accel"

for key in sorted(dsData.keys()):
    print key, dsData[key].entryRoom, dsData[key].exitRoom, dsData[key].accel




"""
# format is timestamp:(exitRoom, entryRoom, occupancy, accelerometer activity)
dsData = {63:DoorSensorReading(1,0,2,1),88:DoorSensorReading(0,1,1,0), 175:DoorSensorReading(1,0,2,1), 189:DoorSensorReading(1,0,1,0),
          195:DoorSensorReading(0,1,1,1), 202:DoorSensorReading(0,1,1,1), 
          99:DoorSensorReading(1,2,2,1), 130:DoorSensorReading(1,2,1,1),149:DoorSensorReading(2,1,2,1), 153:DoorSensorReading(2,1,1,1), 
          163:DoorSensorReading(1,2,2,0), 169:DoorSensorReading(2,1,1,0),
          60:DoorSensorReading(1,3,1,1), 87:DoorSensorReading(1,3,1,0), 95:DoorSensorReading(3,1,1,1), 107:DoorSensorReading(3,1,1,0),
          164:DoorSensorReading(1,3,1,0), 167:DoorSensorReading(3,1,1,0)
          }
          """
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


accelProcFile1 = open("Data_Deployment_9/Relay_Station_10014/Accelerometer/Accelerometer_Synched2016-01-14_15-23.txt", "r")
accelProcFile2 = open("Data_Deployment_9/Relay_Station_9999/Accelerometer/Accelerometer_Synched2016-01-14_15-23.txt", "r")
accelProcFile3 = open("Data_Deployment_9/Relay_Station_10004/Accelerometer/Accelerometer_Synched2016-01-14_15-23.txt", "r")


accelProcFile1 = open("Data_Deployment_9/Relay_Station_10014/Accelerometer/Accelerometer_Synched2016-01-14_13-23.txt", "r")
accelProcFile2 = open("Data_Deployment_9/Relay_Station_9999/Accelerometer/Accelerometer_Synched2016-01-14_13-23.txt", "r")
accelProcFile3 = open("Data_Deployment_9/Relay_Station_10004/Accelerometer/Accelerometer_Synched2016-01-14_13-23.txt", "r")
accelProcFile4 = open("Data_Deployment_9/Relay_Station_10009/Accelerometer/Accelerometer_Synched2016-01-14_13-23.txt", "r")

accelProcFile2 = open("Data_Deployment_9/Relay_Station_9999/Accelerometer/Accelerometer_Synched2016-01-14_13-06.txt", "r")
accelProcFile3 = open("Data_Deployment_9/Relay_Station_10004/Accelerometer/Accelerometer_Synched2016-01-14_13-06.txt", "r")
accelProcFile1 = open("Data_Deployment_9/Relay_Station_10009/Accelerometer/Accelerometer_Synched2016-01-14_13-06.txt", "r")

accelProcFile2 = open("Data_Deployment_9/Relay_Station_9999/Accelerometer/Accelerometer_Synched2016-01-14_15-14.txt", "r")
accelProcFile3 = open("Data_Deployment_9/Relay_Station_10004/Accelerometer/Accelerometer_Synched2016-01-14_15-14.txt", "r")
accelProcFile4 = open("Data_Deployment_9/Relay_Station_10009/Accelerometer/Accelerometer_Synched2016-01-14_15-14.txt", "r")
accelProcFile1 = open("Data_Deployment_9/Relay_Station_10014/Accelerometer/Accelerometer_Synched2016-01-14_15-14.txt", "r")

"""

accelProcFile1 = open("Data_Deployment_16/Relay_Station_10004/Accelerometer/Accelerometer_Synched2016-04-17_11-22.txt", "r")
accelProcFile2 = open("Data_Deployment_16/Relay_Station_9999/Accelerometer/Accelerometer_Synched2016-04-17_11-22.txt", "r")
accelProcFile3 = open("Data_Deployment_16/Relay_Station_10009/Accelerometer/Accelerometer_Synched2016-04-17_11-22.txt", "r")



doorData = []
probDSChange = []

transProb = [[[0]*numStates] for i in range(numStates)]
locProb = [[0]*numStates for i in range(maxTime)]



#root = tk.Tk()
#root.withdraw()

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

if numStates == 5:  
    t_data4, x_data, y_data, z_data, rssi_data4 = plotAccel(accelProcFile4)
    for i in range(len(rssi_data4)):
        if rssi_data4[i] == 0 and x_data[i] == 0:
            rssi_data4[i] = -200
        
        if rssi_data4[i] < -200:
            rssi_data4[i] = -200


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
        
        rssi1 = getRSSIChange(t_data1, t - acceloffset, rssi_data1, scaleF * RSSIDir[0], True)
        rssi2 = getRSSIChange(t_data2, t - acceloffset, rssi_data2, scaleF * RSSIDir[1], True)
        rssi3 = getRSSIChange(t_data3, t - acceloffset, rssi_data3, scaleF * RSSIDir[2], True)
        
        rssi4 = getRSSIChange(t_data1, t - acceloffset, rssi_data1, -1*scaleF * RSSIDir[0], False)
        rssi5 = getRSSIChange(t_data2, t - acceloffset, rssi_data2, -1*scaleF * RSSIDir[1], False)
        rssi6 = getRSSIChange(t_data3, t - acceloffset, rssi_data3, -1*scaleF * RSSIDir[2], False)
        
        if numStates == 5:
            rssi4 = getRSSIChange(t_data4, t, rssi_data4, scaleF * RSSIDir[3], False)
            rssi = max(rssi1, rssi2, rssi3, rssi4)
        else:
            rssi = max(rssi1, rssi2, rssi3)
            rssiWrongDir = max(rssi4, rssi5, rssi6)

        #probChange = ((rssi + dsData[t].accel) + locProb[t-1][exRoom]/dsData[t].occupancy)/2
        
        
        if dsData[t].accel == 0.5 and rssi == 0 and rssiWrongDir == 0:
            rssi = 0.5
            rssiWrongDir = 0.5
            
        probChange = ((rssi + dsData[t].accel))/2.0
        if probChange > 0.9:
            probChange = 0.9
            
        probChangeWrongDir = ((rssiWrongDir + dsData[t].accel))/2.0
        if probChangeWrongDir > 0.9:
            probChangeWrongDir = 0.9
        
        
        probDSChange.append([t, rssi, dsData[t].accel, locProb[t-1][exRoom], probChange])
        dsData[t].probPWD = probChange
        dsData[t].probPWDWrongDir = probChangeWrongDir
        pStay = (1-probChange)
        for j in range(numStates):
            if j == entRoom:
                locProb[t][entRoom] = probChange + pStay*locProb[t-1][entRoom]
            else:
                locProb[t][j] = pStay*locProb[t-1][j]


print probDSChange

"""
############################
# Bluetooth Connection
BT_connection = []
infile = open("BT_localization.txt", "r")

for line in infile.readlines():
    split_line = line.split(",")
    print line
    BT_connection.append((int(split_line[0]), int(split_line[1])))
infile.close()

sortedDSEvents = sorted(dsData.keys())

for i in range(len(sortedDSEvents) - 1):
   

for t in dsData:
    BTroom = findLastBTConnect(BT_connection, t)
    if BTroom ==0:
        BTroom = findNextBTConnect(BT_connection, t)
        
    dsData[t].BTConnectionRoom = BTroom
"""

roomLocations = []
      
location_sequence = viterbi(maxTime, dsData, states, relayStats)

for t in range(maxTime):
    if t in dsData:
        print t, location_sequence[t-1],location_sequence[t], location_sequence[t+1]




        