import logging
import time

from pylgbst import get_connection_auto

logging.basicConfig(level=logging.DEBUG)
conn = get_connection_auto(hub_mac="00:16:53:A0:E0:6B", hub_name="LEGO Move Hub")
conn.enable_notifications()

time.sleep(15) # wait 1 minute to gather info