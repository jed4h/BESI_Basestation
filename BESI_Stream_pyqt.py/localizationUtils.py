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
    def __init__(self, exitRoom, entryRoom, occupancy, accel):
        self.entryRoom = entryRoom
        self. exitRoom = exitRoom
        self.occupancy = occupancy
        self.accel = accel
        self.probPWD = 0
    
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

    # when n door sensor reading is etected, probability of moving to another state is 0 and probability of staying in a state is 1
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