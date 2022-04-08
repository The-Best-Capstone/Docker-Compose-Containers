
from threading import Thread, Event

import numpy as np 

# kafka consumer:
# https://kafka-python.readthedocs.io/en/master/usage.html

class temporaryConsumer(Thread) :

    def __init__(self, topic, group, callback) :
        Thread.__init__(self, daemon=True)
        #
        self.sig = Event()
        self.callback = callback
        try :
            print("Hello World!")
            #consumer = KafkaConsumer(
            #    topic, group_id=group, bootstrap_servers=["localhost:9092"]
            #)
            consumer = None 
        except Exception as e :
            ## TODO: Throw error if consumer throws exception
            pass 
        else : 
            self.consumer = consumer
            self.start() 

    def stop(self) :
        self.sig.set()

    def run(self) :
        count = 0 
        while not self.sig.is_set() :
            ## TODO: constantly read consumer
            self.callback(5*np.sin(count))
            count = count + 0.1
            time.sleep(0.1)