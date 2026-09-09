"""Constants for the UE Boom integration."""

from typing import Final

DOMAIN = "ue_boom"

# Config flow data keys.
CONF_TRUSTED_MAC = "trusted_mac"

# GATT characteristic used to send the magic "power" packet.
# The UE Boom/Megaboom only honors a GATT Write Request (with response)
# written to this characteristic while the speaker is in BLE standby.
POWER_CHARACTERISTIC_UUID: Final = "c6d6dc0d-07f5-47ef-9b59-630622b01fd3"

# Standard Bluetooth battery service characteristic (level in percent).
BATTERY_CHARACTERISTIC_UUID: Final = "00002a19-0000-1000-8000-00805f9b34fb"

# The BLE service the speaker advertises while in standby.
SERVICE_UUID: Final = "0000fe61-0000-1000-8000-00805f9b34fb"

# Manufacturer (company) ID present in the speaker's BLE advertisement.
MANUFACTURER_ID: Final = 3

# Trailing byte of the magic packet.
CMD_POWER_ON: Final = 0x01
# Power off (0x02) is not exposed: it requires classic Bluetooth (RFCOMM),
# which Home Assistant's BLE-only Bluetooth integration cannot do.
CMD_POWER_OFF: Final = 0x02
