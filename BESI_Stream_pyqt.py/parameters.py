
SHIMMER_TICKS = 65536                                   # Shimmer timestamps are the value of a counter that counts up to 65535 at a frequency of 32768 Hz
SHIMMER_FREQ = 32768
SAMPLING_RATE = 102.4                                   # Shimmer Accelerometer sampling rate
TICKS_PER_SAMPLE = int(SHIMMER_FREQ / SAMPLING_RATE)   # Difference between timestamps in consecutive samples from shimmer
TICK_TIME = float(TICKS_PER_SAMPLE) / SHIMMER_FREQ            # time in seconds between sccelerometer samples
ACCEL_PACKET_SIZE = 22                                  # bytes in a single data sample from each sensor
TEMP_PACKET_SIZE = 20
MIC_PACKET_SIZE = 23
LIGHT_PACKET_SIZE = 25
CORRUPTED_COUNT = 16                                    # corrupted transmission 
# Calibration parameters
# Assumes alignment is:    1 0 0
#                          0 1 0
#                          0 0 1
xOff = 2086
yOff = 2048
zOff = 2050
xSens = 84.0
ySens = 83.0
zSens = 83.0

# Paraneters per relay station
PORT0 = 9999
USE_ACCEL0 = True
USE_LIGHT0 = False
USE_ADC0 = False

PORT1 = 10003
USE_ACCEL1 = True
USE_LIGHT1 = True
USE_ADC1 = True