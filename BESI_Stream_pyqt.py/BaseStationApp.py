import stream
import multiprocessing
from parameters import *


if __name__ == '__main__':
    
    
    
    # Create a process for each BeagleBone
    streaming_process1 = multiprocessing.Process(target = stream.stream_process, args=(PORT0, USE_ACCEL0, USE_LIGHT0, USE_ADC0))
    streaming_process2 = multiprocessing.Process(target = stream.stream_process, args=(PORT1, USE_ACCEL1, USE_LIGHT1, USE_ADC1))
    
    streaming_process1.start()
    streaming_process2.start()
   
    streaming_process1.join()
    streaming_process2.join()