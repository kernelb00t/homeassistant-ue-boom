"""Bluetooth communication with a UE Boom speaker."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Final

from bleak_retry_connector import BleakClientWithServiceCache

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import BATTERY_CHARACTERISTIC_UUID, POWER_CHARACTERISTIC_UUID

_LOGGER = logging.getLogger(__name__)

CONNECT_TIMEOUT: Final = 15.0
WRITE_TIMEOUT: Final = 10.0


def build_power_packet(trusted_mac: str, command: int) -> bytes:
    """Build the 7-byte magic packet: <trusted_mac> + <command>."""
    return bytes.fromhex(trusted_mac) + bytes([command])


async def async_send_power_command(
    hass: HomeAssistant, address: str, trusted_mac: str, command: int
) -> None:
    """Connect to the speaker and write the magic power packet over BLE."""
    ble_device = bluetooth.async_ble_device_from_address(
        hass, address.upper(), connectable=True
    )
    if ble_device is None:
        raise HomeAssistantError(
            f"UE Boom speaker {address} is not reachable via Bluetooth"
        )

    packet = build_power_packet(trusted_mac, command)
    client = BleakClientWithServiceCache(ble_device)
    try:
        async with asyncio.timeout(CONNECT_TIMEOUT):
            await client.connect()
        async with asyncio.timeout(WRITE_TIMEOUT):
            # The UE Boom only honors a GATT "Write Request" (with response),
            # not a "Write Without Response".
            await client.write_gatt_char(
                POWER_CHARACTERISTIC_UUID, packet, response=True
            )
        _LOGGER.debug("Sent power command %#04x to %s", command, address)
    except asyncio.TimeoutError as exc:
        raise HomeAssistantError(
            f"Timed out communicating with UE Boom speaker {address}"
        ) from exc
    except Exception as exc:
        raise HomeAssistantError(
            f"Failed to send command to UE Boom speaker {address}: {exc}"
        ) from exc
    finally:
        with contextlib.suppress(Exception):
            await client.disconnect()


async def async_read_battery(hass: HomeAssistant, address: str) -> int | None:
    """Read the battery level (%) from the speaker over BLE.

    Only works while the speaker is in BLE standby (turned off). Returns None
    when the speaker is unreachable or the read fails.
    """
    ble_device = bluetooth.async_ble_device_from_address(
        hass, address.upper(), connectable=True
    )
    if ble_device is None:
        return None

    client = BleakClientWithServiceCache(ble_device)
    try:
        async with asyncio.timeout(CONNECT_TIMEOUT):
            await client.connect()
        async with asyncio.timeout(WRITE_TIMEOUT):
            data = await client.read_gatt_char(BATTERY_CHARACTERISTIC_UUID)
        return int(data[0])
    except Exception:
        return None
    finally:
        with contextlib.suppress(Exception):
            await client.disconnect()
