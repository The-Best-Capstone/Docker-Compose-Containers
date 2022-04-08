#!/usr/bin/python
import RPi.GPIO as GPIO
from kafka import KafkaProducer
from json import dumps

class MAX31855(object):
    '''Python driver for [MAX38155 Cold-Junction Compensated Thermocouple-to-Digital Converter](http://www.maximintegrated.com/datasheet/index.mvp/id/7273)
     Requires:
     - The [GPIO Library](https://code.google.com/p/raspberry-gpio-python/) (Already on most Raspberry Pi OS builds)
     - A [Raspberry Pi](http://www.raspberrypi.org/)

    '''
    def __init__(self, cs_pin, clock_pin, data_pin, units = "c", board = GPIO.BCM):
        '''Initialize Soft (Bitbang) SPI bus

        Parameters:
        - cs_pin:    Chip Select (CS) / Slave Select (SS) pin (Any GPIO)  
        - clock_pin: Clock (SCLK / SCK) pin (Any GPIO)
        - data_pin:  Data input (SO / MOSI) pin (Any GPIO)
        - units:     (optional) unit of measurement to return. ("c" (default) | "k" | "f")
        - board:     (optional) pin numbering method as per RPi.GPIO library (GPIO.BCM (default) | GPIO.BOARD)

        '''
        self.cs_pin = cs_pin
        self.clock_pin = clock_pin
        self.data_pin = data_pin
        # print(f"{self.cs_pin}\n{self.clock_pin}\n{self.data_pin}\n\n")
        self.units = units
        self.data = None
        self.board = board

        # Initialize needed GPIO
        GPIO.setmode(self.board)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.setup(self.clock_pin, GPIO.OUT)
        GPIO.setup(self.data_pin, GPIO.IN)

        # Pull chip select high to make chip inactive
        GPIO.output(self.cs_pin, GPIO.HIGH)

    def get(self):
        '''Reads SPI bus and returns current value of thermocouple.'''
        self.read()
        self.checkErrors()
        return getattr(self, "to_" + self.units)(self.data_to_tc_temperature())

    def get_rj(self):
        '''Reads SPI bus and returns current value of reference junction.'''
        self.read()
        return getattr(self, "to_" + self.units)(self.data_to_rj_temperature())

    def read(self):
        '''Reads 32 bits of the SPI bus & stores as an integer in self.data.'''
        bytesin = 0
        # Select the chip
        GPIO.output(self.cs_pin, GPIO.LOW)
        # Read in 32 bits
        for i in range(32):
            GPIO.output(self.clock_pin, GPIO.LOW)
            bytesin = bytesin << 1
            if (GPIO.input(self.data_pin)):
                bytesin = bytesin | 1
            GPIO.output(self.clock_pin, GPIO.HIGH)
        # Unselect the chip
        GPIO.output(self.cs_pin, GPIO.HIGH)
        # Save data
        self.data = bytesin

    def checkErrors(self, data_32 = None):
        '''Checks error bits to see if there are any SCV, SCG, or OC faults'''
        if data_32 is None:
            data_32 = self.data
        anyErrors = (data_32 & 0x10000) != 0    # Fault bit, D16
        noConnection = (data_32 & 1) != 0       # OC bit, D0
        shortToGround = (data_32 & 2) != 0      # SCG bit, D1
        shortToVCC = (data_32 & 4) != 0         # SCV bit, D2
        if anyErrors:
            if noConnection:
                raise MAX31855Error("No Connection")
            elif shortToGround:
                raise MAX31855Error("Thermocouple short to ground")
            elif shortToVCC:
                raise MAX31855Error("Thermocouple short to VCC")
            else:
                # Perhaps another SPI device is trying to send data?
                # Did you remember to initialize all other SPI devices?
                raise MAX31855Error("Unknown Error")

    def data_to_tc_temperature(self, data_32 = None):
        '''Takes an integer and returns a thermocouple temperature in celsius.'''
        if data_32 is None:
            data_32 = self.data
        tc_data = ((data_32 >> 18) & 0x3FFF)
        return self.convert_tc_data(tc_data)

    def data_to_rj_temperature(self, data_32 = None):
        '''Takes an integer and returns a reference junction temperature in celsius.'''
        if data_32 is None:
            data_32 = self.data
        rj_data = ((data_32 >> 4) & 0xFFF)
        return self.convert_rj_data(rj_data)

    def convert_tc_data(self, tc_data):
        '''Convert thermocouple data to a useful number (celsius).'''
        if tc_data & 0x2000:
            # two's compliment
            without_resolution = ~tc_data & 0x1FFF
            without_resolution += 1
            without_resolution *= -1
        else:
            without_resolution = tc_data & 0x1FFF
        return without_resolution * 0.25

    def convert_rj_data(self, rj_data):
        '''Convert reference junction data to a useful number (celsius).'''
        if rj_data & 0x800:
           without_resolution = ~rj_data & 0x7FF
           without_resolution += 1
           without_resolution *= -1
        else:
             without_resolution = rj_data & 0x7FF
        return without_resolution * 0.0625

    def to_c(self, celsius):
        '''Celsius passthrough for generic to_* method.'''
        return celsius

    def to_k(self, celsius):
        '''Convert celsius to kelvin.'''
        return celsius + 273.15

    def to_f(self, celsius):
        '''Convert celsius to fahrenheit.'''
        return celsius * 9.0/5.0 + 32

    def cleanup(self):
        '''Selective GPIO cleanup'''
        GPIO.setup(self.cs_pin, GPIO.IN)
        GPIO.setup(self.clock_pin, GPIO.IN)

class MAX31855Error(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

if __name__ == "__main__":

    # Multi-chip example
    import time
    time.sleep(5)
    producer = KafkaProducer(
        bootstrap_servers=['191.30.80.101:9092'],
        value_serializer=lambda x: dumps(x).encode('utf-8')
    )

    cs_pins = [2, 3]
    data_pins = {'2': [23, 26, 5, 22], '3': [17, 13, 4]}
    units = "c"

    thermocouples_to_remove = set()
    thermocouples = set()
    for cs_pin in cs_pins:
        temp = data_pins[f'{cs_pin}']
        print(f"CS_PIN: {cs_pin} \t DATA_PINS: {temp}\n")
        if cs_pin == 2:
            clock_pin = 11
        else:
            clock_pin = 9
        for data_pin in data_pins[f'{cs_pin}']:
            thermocouples.add(MAX31855(cs_pin, clock_pin, data_pin, units))
    running = True
    while(running):
        try:
            values = []
            for thermocouple in thermocouples:
                try:
                    # print(f"CS_PIN: {thermocouple.cs_pin} \t CLOCK_PIN: {thermocouple.clock_pin} \t DATA_PIN: {thermocouple.data_pin}\n")
                    rj = thermocouple.get_rj()
                    tc = thermocouple.get()
                    print("tc: {} and rj: {}".format(tc, rj))
                    temp = ['max-chip', thermocouple.cs_pin, thermocouple.clock_pin, thermocouple.data_pin, rj, tc]
                    values.append(temp)
                except MAX31855Error as e:
                    tc = "Error: "+ e.value
                    thermocouples_to_remove.add(thermocouple)
            if len(thermocouples_to_remove) != 0:
                thermocouples = thermocouples - thermocouples_to_remove
                thermocouples_to_remove.clear()

            print("\n\n")
            
            producer.send('max-chip', value=values)
            time.sleep(0.25)
        except KeyboardInterrupt:
            running = False
    for thermocouple in thermocouples:
        thermocouple.cleanup()
