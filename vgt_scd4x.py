# Adapted from `adafruit_scd4x.py` by Wes Kennedy @ Very Good Technologies
# 
# I found during my work on IAQ-BADGE that their implementation was more complicated than necessary for our use-case
# I found it had too many external dependencies for our simple point use-case

import time
import struct
import const
from machine import I2C, Pin

__version__ = "0.0.1"
__repo__ = ""


SCD4X_DEFAULT_ADDR = 0x62
SCD4X_SDA_PIN = 0x4
SCD4X_SCL_PIN = 0x5
_SCD4X_REINIT = const(0x3646)
_SCD4X_FACTORYRESET = const(0x3632)
_SCD4X_FORCEDRECAL = const(0x362F)
_SCD4X_SELFTEST = const(0x3639)
_SCD4X_DATAREADY = const(0xE4B8)
_SCD4X_STOPPERIODICMEASUREMENT = const(0x3F86)
_SCD4X_STARTPERIODICMEASUREMENT = const(0x21B1)
_SCD4X_STARTLOWPOWERPERIODICMEASUREMENT = const(0x21AC)
_SCD4X_READMEASUREMENT = const(0xEC05)
_SCD4X_SERIALNUMBER = const(0x3682)
_SCD4X_GETTEMPOFFSET = const(0x2318)
_SCD4X_SETTEMPOFFSET = const(0x241D)
_SCD4X_GETALTITUDE = const(0x2322)
_SCD4X_SETALTITUDE = const(0x2427)
_SCD4X_SETPRESSURE = const(0xE000)
_SCD4X_PERSISTSETTINGS = const(0x3615)
_SCD4X_GETASCE = const(0x2313)
_SCD4X_SETASCE = const(0x2416)


class SCD4X:
    def __init__(self, i2c_bus, address=SCD4X_DEFAULT_ADDR, sda=Pin(SCD4X_SDA_PIN), scl=Pin(SCD4X_SCL_PIN)):
        self.i2c_device = I2C(scl, Pin.OUT, sda, freq=400000)
        self._buffer = bytearray(18)
        self._cmd = bytearray(2)
        self._crc_buffer = bytearray(2)

        self._temperature = None
        self._relative_humidity = None
        self._co2 = None

        self.stop_periodic_measurement()


    @property
    def CO2(self):
        """Returns values in ppm (parts per million)

        .. note::
            Between measurements, the most recent reading will be cached and returned.

        """
        if self.data_ready:
            self._read_data()
        return self._co2
    
    @property
    def temperature(self):
        """Returns the current temperature in degrees Celsius and Farenheit
        
        .. note::
            Between measurements, the most recent reading will be cached and returned.

            Response is provided as dictionary

        .. code-block:: json

            {
                'temp_c': '23.0',
                'temp_f': '73.4'
            }
        
        """
        if self.data_ready:
            payload = {'temp_c': '','temp_f': ''}

            self._read_data()
            payload['temp_c'] = self._temperature
            payload['temp_f'] = (self._temperature * 1.8) + 32

            return payload

    @property
    def relative_humidity(self):
        """Returns the current relative humidity in %rH.
        
        .. note::
            Between measurements, the most recent reading will be cached and returned.
        
        """
        if self.data_ready:
            self._read_data()
        return self._relative_humidity
    
    @property
    def get_all_data(self):
        """Returns dict payload of all data.
        
        .. note::
            Utilizes cached data from all data types
        
        .. code-block:: json
        
            {
                temperature: {
                    'temp_c': '23.0',
                    'temp_f': '73.4'
                },
                'humid': '41.3',
                'co2': '386'
            }
        
        """
        payload = {}
        payload['temperature'] = self.temperature()
        payload['humid'] = self.relative_humidity()
        payload['co2'] = self.CO2()

        return payload