from json import load, dumps
from time import sleep
from random import uniform
from threading import Thread
from kafka import KafkaProducer

class SensorThread(Thread):
    def __init__(self, current_sensors):
        Thread.__init__(self)
        self.current_sensors = current_sensors
        self.start()

    def run(self):
        init_value = round(uniform(15.000, 300.00), 3)
        counter = 0
        try:
            producer = KafkaProducer(
                bootstrap_servers=['192.168.122.1:9092'],
                value_serializer=lambda x: dumps(x).encode('utf-8')
            )
        except Exception:
            print("EXCEPTION!")
            pass

        while True:
            values = {}
            for sensor in self.current_sensors:
                if (counter % 3 == 0):
                    rand_val = round(init_value + uniform(10.000, 30.000), 3)
                else:
                    rand_val = round(init_value - uniform(5.000, 10.000), 3)
                values[sensor['channel']] = rand_val

            print(values)
            producer.send('analog', value=values)

            init_value = round(init_value + uniform(5.000, 10.000), 3) if counter % 2 == 0 else round(init_value - uniform(5.000, 10.000), 3)
            counter = counter + 1
            # minimum sleep needed when processing dictionaries and writing to timescale like this
            # sleep(0.00625)
            sleep(0.007)

if __name__ == "__main__":
    sleep(15)
    with open("./config.json", "r") as f:
        config = load(f)

    SensorThread(config)
