from json import load, dumps
from time import sleep
from random import uniform
from threading import Thread
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic


class SensorThread(Thread):
    def __init__(self, current_sensors):
        Thread.__init__(self)
        self.current_sensors = current_sensors
        self.start()

    def run(self):
        try:
            producer = KafkaProducer(
                bootstrap_servers=['172.17.0.1:9092'],
                value_serializer=lambda x: dumps(x).encode('utf-8')
            )
        except Exception as ex:
            print(ex)

        while True:
            for sensor in self.current_sensors:
                randInt = round(uniform(15.000, 300.000), 3)
                print(sensor['channel'], randInt)
                producer.send(sensor['topic_name'], value=randInt)
                sleep(0.5)

if __name__ == "__main__":
    with open("./config.json", "r") as f:
        config = load(f)

    SensorThread(config)
