from pylgbst.hub import MoveHub
from pylgbst import get_connection_bleak
from bleak import BleakScanner

HUB_ADDRESS = "00:16:53:A0:E0:6B"  # Replace with your actual hub address

##from pylgbst.hub import MoveHub

##hub = MoveHub()

##for device in hub.peripherals:
  ##  print(device)

def main():
    device = try_connection()
    if device:
        print(f"Connected to device: {device}")
    else:
        print("Failed to connect to the device.")
  

##self.hub = MoveHub(get_connection_bleak(hub_mac = "00:16:53:A0:E0:6B"))

async def try_connection():
    

    HUB_ADDRESS = "00:16:53:A0:E0:6B"  # Replace with your actual hub address
    device = await BleakScanner.find_device_by_address(HUB_ADDRESS)

    if device is None:
        print(f"Device with address {HUB_ADDRESS} not found.")
        return None

    # conn = get_connection_bleak(hub_mac=HUB_ADDRESS)
    # hub = MoveHub(conn)
    
    return device

   