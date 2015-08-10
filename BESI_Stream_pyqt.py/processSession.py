from processParseConfig import processParseConfig
from processAccel import processAccel
from processLight import processLight
from processNoise import processSound
from processTemp import processTemp
from processDoor import processDoor

def processSession(basePort):
    # read config.txt to get the deployment ID
    try:
        DeploymentID = processParseConfig()
    except:
        print "Error reading configuration file"
        
    
    
    try:
        rawAccelFile = open("Data_Deployment_{}/relay_Station_{}/accel{}".format(DeploymentID, basePort, basePort), "r")
        rawLightFile = open("Data_Deployment_{}/relay_Station_{}/light{}".format(DeploymentID, basePort, basePort), "r")
        rawNoiseFile = open("Data_Deployment_{}/relay_Station_{}/sound{}".format(DeploymentID, basePort, basePort), "r")
        rawTempFile = open("Data_Deployment_{}/relay_Station_{}/temp{}".format(DeploymentID, basePort, basePort), "r")
        rawDoorFile = open("Data_Deployment_{}/relay_Station_{}/door{}".format(DeploymentID, basePort, basePort), "r")
    except:
        print "Error opening raw data files"
        
    else:
        # processing is mostly creating timestamps relative to he start of the data collection
        # these functions produce files name sensor ID + date
        fname1, t = processAccel(rawAccelFile, basePort, DeploymentID)
        fname2 = processLight(rawLightFile, basePort, DeploymentID)
        fname3 = processSound(rawNoiseFile, basePort, DeploymentID)
        fname4 = processTemp(rawTempFile, basePort, DeploymentID)
        fname5 = processDoor(rawDoorFile, basePort, DeploymentID)
        
        rawAccelFile.close()
        rawLightFile.close()
        rawNoiseFile.close()
        rawTempFile.close()
        rawDoorFile.close()