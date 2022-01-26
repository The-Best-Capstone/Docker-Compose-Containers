from json import load, dumps
from kafka import KafkaProducer
from time import sleep
from random import uniform
from threading import Thread


class SensorThread(Thread):
    def __init__(self, current_sensor):
        Thread.__init__(self)
        self.current_sensor = current_sensor

    def run(self):
        try:
            producer = KafkaProducer(
                bootstrap_servers=['172.17.0.1:9092'],
                value_serializer=lambda x: dumps(x).encode('utf-8')
            )
        except:
            print("Error!!")

        while True:
            randInt = round(uniform(15.000, 300.000), 3)
            print(self.current_sensor, randInt)
            producer.send('topic_test', value=randInt)
            sleep(1)

if __name__ == "__main__":
    with open("./config.json", "r") as f:
        config = load(f)

    for channel in config:
        SensorThread(channel).start()
