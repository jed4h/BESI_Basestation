import stream
import multiprocessing


if __name__ == '__main__':
    
    
    
    # Create a process for each BeagleBone
    streaming_process1 = multiprocessing.Process(target = stream.stream_process, args=(9999, True, False, False))
    streaming_process2 = multiprocessing.Process(target = stream.stream_process, args=(10003, True, True, True))
    
    streaming_process1.start()
    streaming_process2.start()
   
    streaming_process1.join()
    streaming_process2.join()
