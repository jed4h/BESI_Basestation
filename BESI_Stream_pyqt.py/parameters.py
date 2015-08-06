BIKE_CADENCE = False                                      # run the bike cadence application
SHIMMER_TICKS = 65536                                   # Shimmer timestamps are the value of a counter that counts up to 65535 at a frequency of 32768 Hz
SHIMMER_FREQ = 32768
SAMPLING_RATE = 256                                      # Shimmer Accelerometer sampling rate
TICKS_PER_SAMPLE = int(SHIMMER_FREQ / SAMPLING_RATE)   # Difference between timestamps in consecutive samples from shimmer 320
TICK_TIME = float(TICKS_PER_SAMPLE) / SHIMMER_FREQ            # time in seconds between sccelerometer samples
ACCEL_PACKET_SIZE = 22                                  # bytes in a single data sample from each sensor
TEMP_PACKET_SIZE = 20
MIC_PACKET_SIZE = 24
DOOR_PACKET_SIZE = 31
LIGHT_PACKET_SIZE = 25
CORRUPTED_COUNT = 16                                    # corrupted transmission

# Parameters per relay station
# The port number also acts as a relay station ID
# Port numbers should be 4 apart

class calibSession:
    def __init__(self, xOff, yOff, zOff, xSens, ySens, zSens):
        self.xOff = xOff
        self.yOff = yOff
        self.zOff = zOff
        self.xSens = xSens
        self.ySens = ySens
        self.zSens = zSens
        

"""
PORT0 = 9999
USE_ACCEL0 = True
USE_LIGHT0 = False
USE_ADC0 = False

PORT1 = 10003
USE_ACCEL1 = True
USE_LIGHT1 = True
USE_ADC1 = True
"""