from kafka import KafkaConsumer
from json import loads
from threading import Thread
import datetime
from time import sleep
import psycopg2
from pgcopy import CopyManager

DISGUSTING="191.30.80.101"

class ConsumerThread(Thread):
    def __init__(self, topic):
        Thread.__init__(self)
        self.topic = topic
        self.start()

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
            print(self.topic)
            if self.topic == 'max-chip':
                consumer.subscribe(self.topic)
            else:
                topics = consumer.topics()
                topics.remove('max-chip')
                consumer.subscribe(topics)
        except Exception as e:
            print(e)

        for msg in consumer:
            results = []
            if msg.topic == 'max-chip':
                for item in msg.value:
                    value = (datetime.datetime.now(datetime.timezone.utc), msg.topic, item[1], item[2], item[3], item[4], item[5])
                    print(value)
                    results.append(value)
            else:
                for key, value in msg.value.items():
                    value = (datetime.datetime.now(datetime.timezone.utc), msg.topic, key, value)
                    print(value)
                    results.append(value)

            if (msg.topic == "max-chip"):
                cols = ['time', 'topic', 'chip_select', 'clock_pin', 'data_pin', 'reference_juntion_temperature', 'thermocouple_temperature']
                copyMgr = CopyManager(conn, 'maxchipdata', cols)
                copyMgr.copy(results)
                conn.commit()
            else:
                cols = ['time', 'topic', 'channel', 'data_value']
                copyMgr = CopyManager(conn, 'sensordata', cols)
                copyMgr.copy(results)
                conn.commit()


if __name__ == '__main__':
    sleep(5)
    query_create_sensors_table = "CREATE TABLE IF NOT EXISTS sensors (id serial PRIMARY KEY NOT NULL, type VARCHAR(108));"
    # Query for creating actual sensor data table so we can create a hypertable (Timescale specific)
    query_create_max_chip_table = """CREATE TABLE IF NOT EXISTS maxchipdata (
        time TIMESTAMPTZ NOT NULL,
        topic VARCHAR(108),
        chip_select SMALLINT,
        clock_pin SMALLINT,
        data_pin SMALLINT,
        reference_juntion_temperature DOUBLE PRECISION,
        thermocouple_temperature DOUBLE PRECISION);"""
    query_create_sensor_data_table = """CREATE TABLE IF NOT EXISTS sensordata (
        time TIMESTAMPTZ NOT NULL,
        topic VARCHAR(108),
        channel VARCHAR(108),
        data_value DOUBLE PRECISION);"""
    # Query to create hypertable based on sensordata table
    query_create_sensor_data_hypertable = "SELECT create_hypertable('sensordata', 'time', if_not_exists => TRUE);"
    query_create_max_chip_hypertable = "SELECT create_hypertable('maxchipdata', 'time', if_not_exists => TRUE);" 
    
    # Change this line to connect to the database instance on the local device
    CONNECTION = f"postgres://postgres:testing@{DISGUSTING}:5432/sensorsdb"
    conn = psycopg2.connect(CONNECTION)
    # Create the object to manage our queries
    cursor = conn.cursor()
    
    # Commit those changes in the database
    conn.commit()
    # Create relational table, data table, and hypertable...
    cursor.execute(query_create_sensors_table)
    cursor.execute(query_create_sensor_data_table)
    cursor.execute(query_create_sensor_data_hypertable)
    cursor.execute(query_create_max_chip_table)
    cursor.execute(query_create_max_chip_hypertable)
    conn.commit()
    print("Starting threads")
    available_topics = KafkaConsumer(bootstrap_servers=[f'{DISGUSTING}:9092']).topics()
    if len(available_topics) > 0:
        for topic in available_topics:
            query_simulation_sensor_creation = f"""INSERT INTO sensors (id, type) 
                                                VALUES (DEFAULT, '{topic}') ON CONFLICT DO NOTHING; """
            cursor.execute(query_simulation_sensor_creation)
            conn.commit()
            ConsumerThread(topic)
