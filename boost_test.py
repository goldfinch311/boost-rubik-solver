import time
from time import sleep
from pylgbst import *
from pylgbst.hub import MoveHub
from pylgbst.peripherals import EncodedMotor, TiltSensor, Current, Voltage, COLORS, COLOR_BLACK
from pylgbst import get_connection_bleak

conn = get_connection_bleak(hub_mac='00:16:53:A0:E0:6B:')
movehub = MoveHub(conn)

for device in movehub.peripherals:
    print(device)

movehub.disconnect()