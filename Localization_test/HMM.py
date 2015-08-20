#Hidden Markov Model to determine room location
import random
from generateParameters import *

rooms = ['1', '2', '3', '4']
connections = [[1, 2], [2, 3], [3, 4]]

num_states = 12
DSWeight = 0.7
BTWeight = 1-DSWeight
PTruePos = 0.95     # probability that door sensor is correctly triggered
PFalsePos = 0.01    # probability that door sensor gives a false positive
PBTSameRoom = 0.25     # probability that the Bluetooth is connected to the relay station in the same room
PBTCloseRoom = 0.25   # probability that bluetooth  is connected to the relay station in a neighboring room
emission_probability = [{},{}]

states = generateStates(rooms)

#states = ('12', '13', '14', '21', '23', '24', '31', '32', '34', '41', '42', '43')
 
observations = [['d12', 'c1'], ['d23', 'c1'], ['d34', 'c3'], ['d43', 'c3'], ['d32', 'c3'], ['d21', 'c1'], ['d12', 'c1'], ['d23', 'c1'], ['d34', 'c3'], ['d43', 'c3'], ['d32', 'c3'], ['d21', 'c1']]

start_probability = generateStartProb(states)
transition_probability = generateTransProb(states, connections)
emission_probability = generateEmmProb(states, connections)

#print start_probability
#print transition_probability
#print emission_probability

""" 
start_probability = {'12': 1.0/num_states, '13': 1.0/num_states, '21': 1.0/num_states, 
                     '23': 1.0/num_states, '31': 1.0/num_states, '32': 1.0/num_states, 
                     '14': 1.0/num_states, '24': 1.0/num_states, '34': 1.0/num_states, 
                     '41': 1.0/num_states, '42': 1.0/num_states, '43': 1.0/num_states}

 
transition_probability = {
   '12' : {'12': 1.0/2, '13': 0, '14':0, '21': 1.0/2, '23': 0.01, '24':0.01, '31': 0, '32': 0, '34':0, '41':0, '42':0, '43':0},
   '13' : {'12': 0, '13': 1.0/3, '14':0, '21': 0, '23': 0, '24':0, '31': 0.01, '32': 1.0/3, '34':1.0/3, '41':0, '42':0, '43':0},
   '14' : {'12': 0, '13': 0, '14':0, '21': 0, '23': 0, '24':0, '31': 0, '32': 0, '34':0, '41':0, '42':0, '43':0},
   '21' : {'12': 1.0/2, '13': .01, '14':0, '21': 1.0/2, '23': 0, '24':0, '31': 0, '32': 0, '34':0, '41':0, '42':0, '43':0},
   '23' : {'12': 0, '13': 0, '14':0, '21': 0, '23': 1.0/3, '24':0, '31': 0.01, '32': 1.0/3, '34':1.0/3, '41':0, '42':0, '43':0},
   '24' : {'12': 0, '13': 0, '14':0, '21': 0, '23': 0, '24':1.0/2, '31': 0, '32': 0, '34':0, '41':0.01, '42':0.01, '43':1.0/2},
   '31' : {'12': 1.0/2, '13': 0.01, '14':0, '21': 0, '23': 0, '24':0, '31': 1.0/2, '32': 0, '34':0, '41':0, '42':0, '43':0},
   '32' : {'12': 0, '13': 0, '14':0, '21': 1.0/3, '23': 1.0/3, '24':0.01, '31': 0, '32': 1.0/3, '34':0, '41':0, '42':0, '43':0},
   '34' : {'12': 0, '13': 0, '14':0, '21': 0, '23': 0, '24':0, '31': 0, '32': 0, '34':1.0/2, '41':0, '42':0.01, '43':1.0/2},
   '41' : {'12': 0, '13': 0, '14':0, '21': 0, '23': 0, '24':0, '31': 0, '32': 0, '34':0, '41':0, '42':0, '43':0},
   '42' : {'12': 0, '13': 0, '14':0, '21': 1.0/3, '23': 1.0/3, '24':.01, '31': 0, '32': 0, '34':0, '41':0, '42':1.0/3, '43':0},
   '43' : {'12': 0, '13': 0, '14':0, '21': 0, '23': 0, '24':0, '31': 0.01, '32': 1.0/3, '34':1.0/3, '41':0, '42':0, '43':1.0/3}
   }
 
emission_probability[0] = {
   '12' : {'d12': PTruePos, 'd13': PFalsePos,  'd21': PFalsePos, 'd23': PFalsePos, 'd31': PFalsePos, 'd32': PFalsePos, 'd14': PFalsePos, 'd24': PFalsePos, 'd34': PFalsePos, 'd41': PFalsePos, 'd42': PFalsePos, 'd43': PFalsePos}, 
   '13' : {'d12': PFalsePos, 'd13': PTruePos, 'd21': PFalsePos, 'd23': PFalsePos, 'd31': PFalsePos, 'd32': PFalsePos, 'd14': PFalsePos, 'd24': PFalsePos, 'd34': PFalsePos, 'd41': PFalsePos, 'd42': PFalsePos, 'd43': PFalsePos},
   '14' : {'d12': PFalsePos, 'd13': PFalsePos, 'd21': PFalsePos, 'd23': PFalsePos, 'd31': PFalsePos, 'd32': PFalsePos, 'd14': PTruePos, 'd24': PFalsePos, 'd34': PFalsePos, 'd41': PFalsePos, 'd42': PFalsePos, 'd43': PFalsePos},
   '21' : {'d12': PFalsePos, 'd13': PFalsePos, 'd21': PTruePos, 'd23': PFalsePos, 'd31': PFalsePos, 'd32': PFalsePos, 'd14': PFalsePos, 'd24': PFalsePos, 'd34': PFalsePos, 'd41': PFalsePos, 'd42': PFalsePos, 'd43': PFalsePos},
   '23' : {'d12': PFalsePos, 'd13': PFalsePos, 'd21': PFalsePos, 'd23': PTruePos, 'd31': PFalsePos, 'd32': PFalsePos, 'd14': PFalsePos, 'd24': PFalsePos, 'd34': PFalsePos, 'd41': PFalsePos, 'd42': PFalsePos, 'd43': PFalsePos},
   '24' : {'d12': PFalsePos, 'd13': PFalsePos, 'd21': PFalsePos, 'd23': PFalsePos, 'd31': PFalsePos, 'd32': PFalsePos, 'd14': PFalsePos, 'd24': PTruePos, 'd34': PFalsePos, 'd41': PFalsePos, 'd42': PFalsePos, 'd43': PFalsePos},
   '31' : {'d12': PFalsePos, 'd13': PFalsePos, 'd21': PFalsePos, 'd23': PFalsePos, 'd31': PTruePos, 'd32': PFalsePos, 'd14': PFalsePos, 'd24': PFalsePos, 'd34': PFalsePos, 'd41': PFalsePos, 'd42': PFalsePos, 'd43': PFalsePos},
   '32' : {'d12': PFalsePos, 'd13': PFalsePos, 'd21': PFalsePos, 'd23': PFalsePos, 'd31': PFalsePos, 'd32': PTruePos, 'd14': PFalsePos, 'd24': PFalsePos, 'd34': PFalsePos, 'd41': PFalsePos, 'd42': PFalsePos, 'd43': PFalsePos},
   '34' : {'d12': PFalsePos, 'd13': PFalsePos, 'd21': PFalsePos, 'd23': PFalsePos, 'd31': PFalsePos, 'd32': PFalsePos, 'd14': PFalsePos, 'd24': PFalsePos, 'd34': PTruePos, 'd41': PFalsePos, 'd42': PFalsePos, 'd43': PFalsePos},
   '41' : {'d12': PFalsePos, 'd13': PFalsePos, 'd21': PFalsePos, 'd23': PFalsePos, 'd31': PFalsePos, 'd32': PFalsePos, 'd14': PFalsePos, 'd24': PFalsePos, 'd34': PFalsePos, 'd41': PTruePos, 'd42': PFalsePos, 'd43': PFalsePos},
   '42' : {'d12': PFalsePos, 'd13': PFalsePos, 'd21': PFalsePos, 'd23': PFalsePos, 'd31': PFalsePos, 'd32': PFalsePos, 'd14': PFalsePos, 'd24': PFalsePos, 'd34': PFalsePos, 'd41': PFalsePos, 'd42': PTruePos, 'd43': PFalsePos},
   '43' : {'d12': PFalsePos, 'd13': PFalsePos, 'd21': PFalsePos, 'd23': PFalsePos, 'd31': PFalsePos, 'd32': PFalsePos, 'd14': PFalsePos, 'd24': PFalsePos, 'd34': PFalsePos, 'd41': PFalsePos, 'd42': PFalsePos, 'd43': PTruePos}     
   }
"""
emission_probability[1] = {
   '12' : {'c1': PBTCloseRoom, 'c2': PBTSameRoom, 'c3': PBTCloseRoom, 'c4': PBTCloseRoom},
   '13' : {'c1': PBTCloseRoom, 'c2': PBTCloseRoom, 'c3': PBTSameRoom, 'c4': PBTCloseRoom},
   '14' : {'c1': PBTCloseRoom, 'c2': PBTSameRoom, 'c3': PBTCloseRoom, 'c4': PBTCloseRoom},
   '21' : {'c1': PBTSameRoom, 'c2': PBTCloseRoom, 'c3': PBTCloseRoom, 'c4': PBTCloseRoom},
   '23' : {'c1': PBTCloseRoom, 'c2': PBTCloseRoom, 'c3': PBTSameRoom, 'c4': PBTCloseRoom},
   '31' : {'c1': PBTSameRoom, 'c2': PBTCloseRoom, 'c3': PBTCloseRoom, 'c4': PBTCloseRoom},
   '32' : {'c1': PBTCloseRoom, 'c2': PBTSameRoom, 'c3': PBTCloseRoom, 'c4': PBTCloseRoom},
   '24' : {'c1': PBTCloseRoom, 'c2': PBTSameRoom, 'c3': PBTCloseRoom, 'c4': PBTCloseRoom},
   '34' : {'c1': PBTCloseRoom, 'c2': PBTSameRoom, 'c3': PBTCloseRoom, 'c4': PBTCloseRoom},
   '41' : {'c1': PBTCloseRoom, 'c2': PBTSameRoom, 'c3': PBTCloseRoom, 'c4': PBTCloseRoom},
   '42' : {'c1': PBTCloseRoom, 'c2': PBTSameRoom, 'c3': PBTCloseRoom, 'c4': PBTCloseRoom},
   '43' : {'c1': PBTCloseRoom, 'c2': PBTSameRoom, 'c3': PBTCloseRoom, 'c4': PBTCloseRoom}
   }

def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]
    path = {}
 
    # Initialize base cases (t == 0)
    for y in states:
        V[0][y] = start_p[y] * emit_p[0][y][obs[0][0]]*emit_p[1][y][obs[0][1]]
        path[y] = [y]
 
    # Run Viterbi for t > 0
    for t in range(1, len(obs)):
        V.append({})
        newpath = {}
 
        for y in states:
            (prob, state) = max((V[t-1][y0] * trans_p[y0][y] * emit_p[0][y][obs[t][0]] * emit_p[1][y][obs[t][1]], y0) for y0 in states)
            V[t][y] = prob
            newpath[y] = path[state] + [y]
 
        # Don't need to remember the old paths
        path = newpath
    n = 0           # if only one element is observed max is sought in the initialization values
    if len(obs) != 1:
        n = t
    print_dptable(V)
    (prob, state) = max((V[n][y], y) for y in states)
    return (prob, path[state])
 
# Don't study this, it just prints a table of the steps.
def print_dptable(V):
    s = "    " + " ".join(("%7d" % i) for i in range(len(V))) + "\n"
    for y in V[0]:
        s += "%.5s: " % y
        s += " ".join("%.7s" % ("%f" % v[y]) for v in V)
        s += "\n"
    #print(s)

#for obs in observations:
#    if random.uniform(0,1) < 0.05:
#        observations.remove(obs)
#        
#print len(observations)
 
def example():
    return viterbi(observations,
                   states,
                   start_probability,
                   transition_probability,
                   emission_probability)
print(example())
