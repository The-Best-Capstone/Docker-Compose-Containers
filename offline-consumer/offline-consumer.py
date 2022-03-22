from kafka import KafkaConsumer
from json import loads
from threading import Thread
import datetime
import csv
import os

DISGUSTING="192.168.122.1"

class ConsumerThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print(self)
        try:
            consumer = KafkaConsumer(
                bootstrap_servers=[f'{DISGUSTING}:9092'],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='my-group-id',
                value_deserializer=lambda x: loads(x.decode('utf-8'))
            )
            print(consumer.topics())
            consumer.subscribe(consumer.topics())
        except Exception as e:
            print(e)
            exit(0)

        for msg in consumer:
            results = []
            for key, value in msg.value.items():
                value = (datetime.datetime.now(datetime.timezone.utc), msg.topic, key, value)
                print(value)
                results.append(value)
    
            fields = ['Time', 'Topic', 'Sensor', 'Value'];

            with open('/media/god/60A0EDAEA0ED8ABC/Testing/sensor_data', 'a') as f:
                # using csv.writer method from CSV package
                write = csv.writer(f)
                  
                write.writerow(fields)
                write.writerows(results)


if __name__ == '__main__':
    if os.path.exists('/media/god/60A0EDAEA0ED8ABC/Testing/sensor_data'):
        os.remove('/media/god/60A0EDAEA0ED8ABC/Testing/sensor_data')

    for worker in range(6):
        ConsumerThread().start()