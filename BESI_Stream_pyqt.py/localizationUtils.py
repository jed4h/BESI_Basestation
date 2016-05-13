import math
from os import listdir
from processDoor import plotDoor, plotDoorStartTime
from processAccel import plotAccel, plotAccelStartTime
from processTemp import  lowPassFilter

def time_to_index(t_data, time):
    value = min(t_data, key=lambda x:abs(x-time))       
    return t_data.index(value)

def rssi_change(t_data, time, rssi_data):
    time_range = 10
    event_index = time_to_index(t_data, time)
    
    if (time -1*time_range > 0):
        start_index = time_to_index(t_data, time - time_range)
    else:
        start_index = 0
        
    end_index = time_to_index(t_data, time + time_range)
    
    if len(rssi_data[start_index:event_index]) != 0:
        start_rssi = sum(rssi_data[start_index:event_index])/len(rssi_data[start_index:event_index])
    else:
        start_rssi = -200
        
    if len(rssi_data[event_index:end_index]) != 0:
        end_rssi = sum(rssi_data[event_index:end_index])/len(rssi_data[event_index:end_index])
    else:
        end_rssi = -200
       
    return start_rssi,end_rssi

class DoorSensorReading:
    def __init__(self, exitRoom, entryRoom, accel):
        self.entryRoom = entryRoom
        self. exitRoom = exitRoom
        self.accel = accel
        self.probPWD = 0
        self.probPWDWrongDir = 0
    
def viterbi(maxTime, dsData, states, relay_stat_states):
    # states for rooms 0-4 (4 is outside)
    
    obs = [1]*maxTime
    start_p = {}
    emit_p = {}
    trans_p = {}
    
    # assumes start state is unknown and is equally likely to be any room
    for s in states:
        start_p[s] = 1.0/len(states)
        emit_p[s] = {}
        trans_p[s] = {}
    
    # emission probability is the relay station the Shimmer is connected to. For now equally distributed between all possible relay stations    
    for s in states:
        for r in relay_stat_states:
            emit_p[s][r] = 1.0/len(relay_stat_states)

    # when no door sensor reading is detected, probability of moving to another state is 0 and probability of staying in a state is 1
    for x in states:
        for y in states:
            if x == y:
                trans_p[x][y] = 1
            else:
                trans_p[x][y] = 0
    
    V = [{}]
    path = {}
 
    # Initialize base cases (t == 0)
    for y in states:
        V[0][y] = start_p[y] * emit_p[y][obs[0]]
        path[y] = [y]
    
    
    # Run Viterbi for t > 0
    for t in range(1,maxTime):
        V.append({})
        newpath = {}
        
        # update transition probability
        if t in dsData:
            
            
            
            entRoom = dsData[t].entryRoom
            exRoom = dsData[t].exitRoom
            probLeave = dsData[t].probPWD
            probStay = (1-probLeave)
            for x in states:
                for y in states:
                    if x == y:
                        trans_p[x][y] = probStay
                    elif x == exRoom and y == entRoom:
                        trans_p[x][y] = probLeave 
                    #direction is wrong   
                    elif x == entRoom and y == exRoom:
                        trans_p[x][y] = dsData[t].probPWDWrongDir * 0.5
                    else:
                        trans_p[x][y] = 0
        
            """
            else:
                for x in states:
                    for y in states:
                        if x == y:
                            trans_p[x][y] = 1
                        else:
                            trans_p[x][y] = 0
            """    

            for y in states:
                (prob, state) = max((V[t-1][y0] * trans_p[y0][y] * emit_p[y][obs[t]], y0) for y0 in states)
                V[t][y] = prob
                newpath[y] = path[state] + [y]

            # Don't need to remember the old paths
            path = newpath
        
        else:
            for y in states:
                (prob, state) = (V[t-1][y], y)
                V[t][y] = prob
                newpath[y] = path[state] + [y]

            # Don't need to remember the old paths
            path = newpath
    
    # Return the most likely sequence over the given time frame
    n = 0           # if only one element is observed max is sought in the initialization values
    if len(obs) != 1:
        n = t
    print_dptable(V)
    (prob, state) = max((V[n][y], y) for y in states)
    return path[state]

# Don't study this; it just prints a table of the steps.
def print_dptable(V):
    yield "    "
    yield " ".join(("%7d" % i) for i in range(len(V)))
    yield "\n"
    for y in V[0]:
        yield "%.5s: " % y
        yield " ".join("%.7s" % ("%f" % v[y]) for v in V)
        yield "\n"


# retuns a value between 0 and 1 that indicates he likelihood of a transition based on changes in the RSSi       
def getRSSIChange(t_data, event, rssi_data, expDir, toPrint):
    start_rssi, end_rssi = rssi_change(t_data, event, rssi_data)
    x = end_rssi - start_rssi
    
    
    if expDir != 0:
        x = expDir * x 
    
        if x < 0:
            y = 0
        elif x <= 10:
            y = 0.75 * x/10.0
        elif x > 10 and x < 40:
            y =  0.75
        else:
            y = 1
        
    elif expDir == 0:
        y = 0.2
    
    if toPrint:   
        print "Time: {} Start RSSI: {} End RSSI: {}  expDir: {} Y: {}".format(event, start_rssi, end_rssi, expDir, y)    
    return y

def getAccelChange(t):
    return 1

#returns the calibrated magnitude from individual accelerometer axes
def accelCalibMag(x_data, y_data, z_data):
    sens = 84
    offset = 2048
    mag = []
    for i in range(len(x_data)):
        # all 0s indicates no connected
        if x_data[i] == 0 and y_data[i] == 0 and z_data[i] == 0:
            mag.append(9.8)
        else:
            mag.append(math.sqrt(((x_data[i]-offset)/sens)**2 + ((y_data[i]-offset)/sens)**2 + ((z_data[i]-offset)/sens)**2))
    
    return mag
    
# taken from someone's matlab code maybe
def teagerCompute(data, returnArray = False):
    L = len(data)
    # assume L is even?
    startPoint = L/2 - 1
    base = data[startPoint]**2
    teager = 0
    
    for i in range(1,startPoint + 1):
        teager+= abs(base - data[startPoint-i]*data[startPoint+i])
        
    # returning an array of the same size as the input makes plotting easier
    if returnArray:    
        return [teager]*L
    else:
        return teager
    
def computeVar(magData, offset = 9.8):
    magVar = [] 
    for val in magData:
        magVar.append(abs(val-offset))
        
    return magVar


# finds the index of the value in teagerList corresponding to the time eventTime
# accel_t_data is the timestamps for the accelerometer, 
#accel_window_size is the number of accel data points used, and Fs is the accel sampling frequency
def findAccelIndex(eventTime, teagerList, accel_t_data, accel_window_size):
    
    # find the index of eventTime in accel data
    tIndex = min(range(len(accel_t_data)), key=lambda i: abs(accel_t_data[i] - eventTime))
    
    return tIndex/accel_window_size

def combineAccelFiles(DeploymentID, port, startTime):
    fname = "Data_Deployment_{0}/Relay_Station_{1}/Accelerometer_Synched{2}.txt".format(DeploymentID, port, startTime, DeploymentID)
    outputFile = open(fname, "w")
    
    t_data, x_data, y_data, z_data, rssi_data = concatAccel(DeploymentID, port, 1.0)
    
    for i in range(len(t_data)):
        outputFile.write("{0:.5f},{1},{2},{3},{4}\n".format(t_data[i], x_data[i], y_data[i], z_data[i], rssi_data[i]))
        
    outputFile.close()


def combineDSFiles(DeploymentID, port, startTime):
    fname = "Data_Deployment_{0}/Relay_Station_{1}/Door Sensor_Synched{2}.txt".format(DeploymentID, port, startTime, DeploymentID)
    outputFile = open(fname, "w")
    
    t_data = []
    door_data1 = []
    door_data2 = []
    
    concatDoor(DeploymentID, port, door_data1, door_data2, t_data)
    
    for i in range(len(t_data)):
        outputFile.write("{0:.2f},{1:.2f},{2:.2f}\n".format(t_data[i], door_data1[i], door_data2[i]))
        
    outputFile.close()
    
def processDSFile(deployID, relayID, door1_data_unfiltered, door2_data_unfiltered, tdoor_data, startDatetime, multiFile = False):
    basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayID) + "/"
    
    if not multiFile:
        doorProcFile = open(basePath + "Door/" + "Door Sensor_Synched" + startDatetime, "r")
        tdoor_data_tmp, door1_data_tmp, door2_data_tmp = plotDoor(doorProcFile)
        
        for tValue in tdoor_data_tmp:
            tdoor_data.append(tValue)
        
        for doorValue in door1_data_tmp:
            door1_data_unfiltered.append(doorValue)
            
        for doorValue in door2_data_tmp:
            door2_data_unfiltered.append(doorValue)
            
        doorProcFile.close()
    
    else:
        concatDoor(deployID, relayID, door1_data_unfiltered, door2_data_unfiltered, tdoor_data)
        
    
def channelDiff(door1_data, door2_data, door_diff):
    for i in range(len(door1_data)):
        door_diff.append(abs(door1_data[i]-door2_data[i]))
        
# finds the start point for a given transition in both channels
def findStartDirection(chan1Data, chan2Data, thresholdHigh, thresholdLow):
    for i in range(len(chan1Data) - 3):
        if chan1Data[i] > thresholdHigh:
            if min(chan1Data[i:i+3]) >= thresholdLow:
                return 1
        elif chan2Data[i] > thresholdHigh:
            if min(chan2Data[i:i+3]) >= thresholdLow:
                return 2
        
        

# creates a list of door sensor transitions to be used in the localization algorithm        
def generateTransitions(door1_data, door2_data, dsTransitions, window_size, tdoor_data, currRoom, nextRoom, goodChannels, onePointDeriv1, onePointDeriv2):
    dsData = {}
    
    
    
    for element in dsTransitions:
        eventIndex = max([element[0], element[1]])
        if goodChannels == 2:
            
            #if element[0] != element[1]:
            #   eventIndex -= window_size/2
            if element[0] == element[1]:
                eventIndex -= window_size/2
            
            
        eventTime = tdoor_data[eventIndex]
        
        direction_window_size = int(window_size * 1.5)
        
        if goodChannels == 2:
            
            direction = findStartDirection(onePointDeriv1[eventIndex-direction_window_size:eventIndex + direction_window_size], onePointDeriv2[eventIndex-direction_window_size:eventIndex + direction_window_size], 1, 0)
            
        elif goodChannels == 1:
            direction = derivSign(door2_data[eventIndex-direction_window_size:eventIndex + direction_window_size], 0.1)
            
        elif goodChannels == 0:
            direction = derivSign(door1_data[eventIndex-direction_window_size:eventIndex + direction_window_size], 0.1)
                
        if direction == 1:
            dsData[round(eventTime)] = DoorSensorReading(nextRoom, currRoom, 0)
        else:
            dsData[round(eventTime)] = DoorSensorReading(currRoom, nextRoom, 0)
    
    return dsData


# returns two lists, one for each channel, with the average distance between points in every window
# also returns the pointwise difference between the lists
# the arrays returned are the same size as the input        
def calcDoorDeriv(door1_data, door2_data, tdoor_data, door1_deriv, door2_deriv, door_diff, diff_deriv, window_size, avgRange):
    door2_avg = average(door2_data[0:window_size*avgRange])
    door1_avg = average(door1_data[0:window_size*avgRange])
    
    for i in range(len(door2_data)/window_size + 1):
        if i%avgRange == 0 and i > 0:
            door2_avg = average(door2_data[(i-avgRange/2)*window_size:(i+avgRange/2)*window_size])
            door1_avg = average(door1_data[(i-avgRange/2)*window_size:(i+avgRange/2)*window_size])
            
        try:
            door1_deriv += avgDeriv(door1_data[i*window_size:i*window_size + window_size], door1_avg, tdoor_data[i*window_size])
        except:
            door1_deriv += avgDeriv(door1_data[i*window_size:-1], door1_avg, tdoor_data[(i-1)*window_size])
            
            
        try:
            door2_deriv += avgDeriv(door2_data[i*window_size:i*window_size + window_size], door2_avg, tdoor_data[i*window_size])
        except:
            door2_deriv += avgDeriv(door2_data[i*window_size:-1], door2_avg, tdoor_data[(i-1)*window_size])
           
            
        try:
            diff_deriv += avgDeriv(door_diff[i*window_size:i*window_size + window_size], 0, tdoor_data[i*window_size])
        except:
            diff_deriv += avgDeriv(door_diff[i*window_size:-1], 0, tdoor_data[(i-1)*window_size]) 
            

# removes door sensor positives where both channels move together (due o noise)            
def filterNoisePeaks(dsTransitions, diff_deriv, goodChannels):
    
    temp = []
    # only remove peaks if both channels supply good data
    if goodChannels == 2:
        for element in dsTransitions:
            # if both door sensor channels move at the dame time, it is likely noise
            #print tdoor_data[element],element,diff_deriv[element]
            if diff_deriv[min(element[0], element[1])] < 2:
                temp.append(element)
           
        for element in temp:
            dsTransitions.remove(element)
        

def avgEnergy(door_data, door_data_avg, startTime):
    energy = 0
    
    # door data is 5? seconds of data    
    for element in door_data:
        #if element < door_data_avg:
        energy += (abs(element - door_data_avg)**2)
        #else:
        #   energy.append(0)
            
    # return an array of the same length for plotting    
    return [energy/100.0]*len(door_data)

# find the average distance between points in door_data
def avgDeriv(door_data, door_data_avg, startTime):
    
    if len(door_data) > 0:
        deriv = 0
        lastPoint = door_data[0]
        
        # door data is 5? seconds of data    
        for element in door_data:
            #if element < door_data_avg:
            deriv += (math.sqrt((element - lastPoint)**2))
            lastPoint = element
            #else:
            #   energy.append(0)
                
        # return an array of the same length for plotting    
        return [deriv]*len(door_data)
    
    else:
        return []

# determines if the derivative of the signal goes above or below a threshold first  
def derivSign(door_data, threshold):
    derivList = []
    lastPoint = door_data[0]
    
    for element in door_data:
        deriv = element - lastPoint
        derivList.append(deriv)
        
        if deriv > threshold:
            return 1
        elif deriv < (threshold * -1):
            return 2
        
        lastPoint = element

    #return derivList

# computes area under the curve relative to avg
def avgInteral(data, avg):
    integ = 0
    
    # door data is 5? seconds of data    
    for val in data:
        integ += val-avg
    
    # return an array of the same size as input        
    return [integ] * len(data)
    

def average(data):
    if len(data) > 0:
        return sum(data)/len(data)
    else:
        return 0;

# compares ground truth entry/exit time to generated times  
def groudtruthCheck(groundTruth, door_data):
    for i in range(len(groundTruth)):
        if abs(groundTruth[i] - door_data[i]) > 2:
            print groundTruth[i],door_data[i]
            return
        
def concatDoor(deployID, relayID, door_data1, door_data2, t_data):
    basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayID) + "/"
    lastStartTime = 0
    totalOffset = 0
    offset = 0
    
    for fileName in  listdir(basePath + "Door"):
        #print basePath + "Door/" + fileName
        doorProcFile = open(basePath + "Door/" + fileName, "r")
        tdoor_data_tmp, door_data_tmp1, door_data_tmp2, startTime = plotDoorStartTime(doorProcFile)
        
        if lastStartTime != 0:
            offset = startTime - lastStartTime
            offset = offset.days * 86400 + offset.seconds + offset.microseconds/1000000.0
            #print offset
               
        if tdoor_data_tmp[0] < 5:
            totalOffset = totalOffset + offset
            lastStartTime = startTime
        
    
        # average sound every second
        for i in range(len(tdoor_data_tmp)):
            t_data.append((tdoor_data_tmp[i] + totalOffset))
            door_data1.append(door_data_tmp1[i])
            door_data2.append(door_data_tmp2[i])
        doorProcFile.close()
        
def concatAccel(deployID, relayID, timeScale=3600):
    basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayID) + "/"
    lastStartTime = 0
    totalOffset = 0
    offset = 0
    t_data = []
    x_data = []
    y_data = []
    z_data = []
    rssi_data = []
    
    for fileName in  listdir(basePath + "Accelerometer"):
        print "Processing {}".format(fileName)
        accelProcFile = open(basePath + "Accelerometer/" + fileName, "r")
        taccel_data_tmp, x_data_tmp, y_data_tmp, z_data_tmp, rssi_data_tmp, startTime = plotAccelStartTime(accelProcFile)
        
        if lastStartTime != 0:
            offset = startTime - lastStartTime
            offset = offset.days * 86400 + offset.seconds + offset.microseconds/1000000.0
        
        # file starts at time 0        
        if taccel_data_tmp[0] < 5:
            totalOffset = totalOffset + offset
            lastStartTime = startTime
        
        for tValue in taccel_data_tmp:
            t_data.append((tValue + totalOffset)/timeScale)
        
        for val in x_data_tmp:
            x_data.append(val)
            
        for val in y_data_tmp:
            y_data.append(val)
            
        for val in z_data_tmp:
            z_data.append(val)
            
        for val in rssi_data_tmp:
            rssi_data.append(val)
            
        accelProcFile.close()
       
    return t_data, x_data, y_data, z_data, rssi_data

# dsData is a list of dicts
def combineDSdata(dsData):
    fullDSdict = {}
    for dsDict in dsData:
        for TSKey in dsDict.keys():
            val = dsDict[TSKey]
            while TSKey in fullDSdict:
                TSKey += 1
            fullDSdict[TSKey] = val
            
    return fullDSdict


# finds times when both door sensors are triggered within 1 second
# door1 and door2 hold times when one of the door sensor channels is triggered 
# values in door1 and door2 are sorted low to high
def findDSTransitions(door1, door2, max_distance, goodChannels = 2):
    # maximum number of samples between two peaks of the same door entry event
    door1Ptr = 0
    door2Ptr = 0
    transitions = []
    
    # both channels give good data
    if goodChannels == 2:
        while((door1Ptr < len(door1)) and (door2Ptr < len(door2))):
            # find the first peak
            if door1[door1Ptr] > door2[door2Ptr]:
                # check if the other sensor had a peak within 1 second (10 samples)
                if (door1[door1Ptr] - door2[door2Ptr]) <= max_distance:
                    transitions.append((door1[door1Ptr],door2[door2Ptr], 2))
                    # peaks in both data are part of the same event
                    #print door1[door1Ptr],door2[door2Ptr]
                    door1Ptr += 1
                    door2Ptr += 1
                else:
                    door2Ptr += 1
                    
            elif door1[door1Ptr] < door2[door2Ptr]:
                # check if the other sensor had a peak within 1 second (10 samples)
                if (door2[door2Ptr] - door1[door1Ptr]) <= max_distance:
                    transitions.append((door1[door1Ptr],door2[door2Ptr], 1))
                    #print door2[door2Ptr],door1[door1Ptr]
                    # peaks in both data are part of the same event
                    door1Ptr += 1
                    door2Ptr += 1
                else:
                    door1Ptr += 1
                    
            else:
                if (door1[door1Ptr] - door2[door2Ptr]) <= max_distance:
                    transitions.append((door1[door1Ptr],door2[door2Ptr], 0))
                    # peaks in both data are part of the same event
                    #print door1[door1Ptr],door2[door2Ptr]
                    door1Ptr += 1
                    door2Ptr += 1
                else:
                    door2Ptr += 1
    
    # only channel 2 gives good data               
    elif goodChannels == 1:
        for event in door2:
            transitions.append((event, event, 0))
    # only     
    elif goodChannels == 0:
        for event in door1:
            transitions.append((event, event, 0))
        
    return transitions      

# find the peaks when the signal is above threshHigh
# the signal needs to fall below threshLow before another peak is detected
# mpd is the minimum distance between peaks (in samples)
def peakDetect(threshHigh, lastPeakThresh, mpd, data, windowSize):
    
    peaks = []
    #peakActive = False
    
    for i in range(len(data) - windowSize):
        # check if a data point is a candidate to be a peak
        if data[i] > threshHigh:
            # check for mpd
            if len(peaks) == 0 and data[i] >= data[i-1] + lastPeakThresh and data[i] >= data[i+windowSize] + lastPeakThresh:
                peaks.append(i)
            elif len(peaks) != 0 and (i >= peaks[-1] + mpd) and data[i] >= data[i-1] + lastPeakThresh and data[i] >= data[i+windowSize] + lastPeakThresh:
                peaks.append(i)
            
            
    return peaks
def processAccelFile(fname):
    #fname1 = tkFileDialog.askopenfilename()
    
    # plot<sensor> functions take the processed file and return arrays to plot
    if fname != None:
        accelProcFile = open(fname, "r")
        #accelProcFile = open("data/Accelerometer2015-07-06_15-18", "r")
        t_data, x_data, y_data, z_data, rssi_data = plotAccel(accelProcFile)
        
    return t_data, x_data, y_data, z_data

def getDSEvents(deployID, relayID, startDateTime, peakThreshold, window_size, avgRange, goodChannels, currRoom, nextRoom):
    tdoor_data = []
    door1_data_unfiltered = []
    door2_data_unfiltered = []
    door1_deriv = []
    door2_deriv = []
    door_diff = []
    diff_deriv = []

    processDSFile(deployID, relayID, door1_data_unfiltered, door2_data_unfiltered, tdoor_data, startDateTime)
         
    # LPF data
    door1_data = lowPassFilter(door1_data_unfiltered)
    door2_data = lowPassFilter(door2_data_unfiltered)
    
    channelDiff(door1_data, door2_data, door_diff)
    
    onePointDeriv1 = [0]
    onePointDeriv2 = [0]
    
    #do single point derivative
    for i in range(1,len(door1_data)):
        onePointDeriv1.append(avgDeriv(door1_data[i-1:i+1], 0, 0)[0])
        
    for i in range(1,len(door2_data)):
        onePointDeriv2.append(avgDeriv(door2_data[i-1:i+1], 0, 0)[0])
    
    calcDoorDeriv(door1_data, door2_data, tdoor_data, door1_deriv, door2_deriv, door_diff, diff_deriv, window_size, avgRange)
    

    # arguments are peakDetect(minPeakHeight, minHeightOverLastPoint, minPeakDistance, data)
    chan1_peaks = peakDetect(peakThreshold, 0.1, 30, door1_deriv, window_size)
    chan2_peaks = peakDetect(peakThreshold, 0.1, 30, door2_deriv, window_size)
    
    dsTransitions = findDSTransitions(chan1_peaks, chan2_peaks, 30, goodChannels)

    filterNoisePeaks(dsTransitions, diff_deriv, goodChannels)
    
    
    dsData = generateTransitions(door1_data, door2_data, dsTransitions, window_size, tdoor_data, currRoom, nextRoom, goodChannels, onePointDeriv1, onePointDeriv2)
    return dsData
            

    
#combineAccelFiles(16, 10004, "2016-04-17_11-22")
#combineDSFiles(16, 10004, "2016-04-17_11-22")
