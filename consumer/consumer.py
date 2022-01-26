from kafka import KafkaConsumer
from json import loads
from time import sleep
from threading import Thread
import datetime
from multiprocessing import Process
import psycopg2
from pgcopy import CopyManager

query_create_sensors_table = "CREATE TABLE sensors (id serial PRIMARY KEY NOT NULL, type VARCHAR(108));"
# Query for creating actual sensor data table so we can create a hypertable (Timescale specific)
query_create_sensor_data_table = """CREATE TABLE sensordata (
    time TIMESTAMPTZ NOT NULL,
    topic VARCHAR(108),
    data_value DOUBLE PRECISION);"""
# Query to create hypertable based on sensordata table
query_create_sensor_data_hypertable = "SELECT create_hypertable('sensordata', 'time')"

CONNECTION = "postgres://god:testing@172.17.0.1:5432/postgres"
conn = psycopg2.connect(CONNECTION)
# Create the object to manage our queries
cursor = conn.cursor()
#
# Remove all tables created in previous test...
cursor.execute("DROP TABLE IF EXISTS sensordata")
cursor.execute("DROP TABLE IF EXISTS sensors")
# Commit those changes in the database
conn.commit()
# Create relational table, data table, and hypertable...
cursor.execute(query_create_sensors_table)
cursor.execute(query_create_sensor_data_table)
cursor.execute(query_create_sensor_data_hypertable)

conn.commit()

for topic in KafkaConsumer(bootstrap_servers=['172.17.0.1:9092']).topics():
    print(topic)
    query_simulation_sensor_creation = f"""INSERT INTO sensors (id, type) 
                                        VALUES (DEFAULT, '{topic}') ON CONFLICT DO NOTHING; """
    cursor.execute(query_simulation_sensor_creation)
    conn.commit()


class ConsumerThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print(self)
        try:
            consumer = KafkaConsumer(
                bootstrap_servers=['172.17.0.1:9092'],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='my-group-id',
                value_deserializer=lambda x: loads(x.decode('utf-8'))
            )
            print(consumer.topics())
            consumer.subscribe("topic_test")
        except:
            print("Error!!")

        for msg in consumer:
            value = (datetime.datetime.now(datetime.timezone.utc), msg.topic, msg.value)
            print(value)
            cols = ['time', 'topic', 'data_value']
            copyMgr = CopyManager(conn, 'sensordata', cols)
            copyMgr.copy((value, ))
            conn.commit()


for worker in range(8):
    ConsumerThread().start()
